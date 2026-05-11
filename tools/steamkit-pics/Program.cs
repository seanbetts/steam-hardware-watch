using System.Text.Json;
using System.Text.Json.Serialization;
using SteamKit2;

var options = Args.Parse(args);
Directory.CreateDirectory(options.OutDir);
Directory.CreateDirectory(Path.GetDirectoryName(options.ReportPath) ?? ".");
Directory.CreateDirectory(Path.GetDirectoryName(options.KeyLinesPath) ?? ".");

var username = Env("STEAMKIT_USERNAME");
var password = Env("STEAMKIT_PASSWORD");
var accessToken = Env("STEAMKIT_ACCESS_TOKEN");
var authCode = Env("STEAMKIT_AUTH_CODE");
var twoFactorCode = Env("STEAMKIT_TWO_FACTOR_CODE");
var timeoutSeconds = int.TryParse(Env("STEAMKIT_TIMEOUT_SECONDS"), out var parsedTimeout)
    ? parsedTimeout
    : 90;

if (string.IsNullOrWhiteSpace(username) || (string.IsNullOrWhiteSpace(password) && string.IsNullOrWhiteSpace(accessToken)))
{
    throw new InvalidOperationException("STEAMKIT_USERNAME and STEAMKIT_PASSWORD or STEAMKIT_ACCESS_TOKEN are required.");
}

using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(timeoutSeconds));
var snapshot = await PicsClient.FetchAsync(username, password, accessToken, authCode, twoFactorCode, cts.Token);

var jsonOptions = new JsonSerializerOptions
{
    WriteIndented = true,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
};

await File.WriteAllTextAsync(
    Path.Combine(options.OutDir, "pics-product-info.json"),
    JsonSerializer.Serialize(snapshot, jsonOptions) + Environment.NewLine,
    cts.Token
);

var rows = ReportRows.Build(snapshot);
await File.WriteAllLinesAsync(options.ReportPath, rows.Select(row => string.Join('\t', row.Select(CleanTsv))), cts.Token);

var keyLines = new List<string> { "SteamKit/PICS package snapshot:" };
keyLines.AddRange(rows.Take(40).Select(row => string.Join('\t', row.Select(CleanTsv))));
await File.WriteAllLinesAsync(options.KeyLinesPath, keyLines, cts.Token);

static string? Env(string name) => Environment.GetEnvironmentVariable(name);

static string CleanTsv(string? value) => (value ?? "").Replace('\t', ' ').Replace('\n', ' ').Trim();

sealed record Args(string OutDir, string ReportPath, string KeyLinesPath)
{
    public static Args Parse(string[] args)
    {
        var values = new Dictionary<string, string>(StringComparer.Ordinal);
        for (var index = 0; index < args.Length; index++)
        {
            if (!args[index].StartsWith("--", StringComparison.Ordinal))
            {
                continue;
            }

            if (index + 1 >= args.Length)
            {
                throw new ArgumentException($"Missing value for {args[index]}.");
            }

            values[args[index]] = args[++index];
        }

        return new Args(
            Require(values, "--out-dir"),
            Require(values, "--report"),
            Require(values, "--key-lines")
        );
    }

    static string Require(Dictionary<string, string> values, string key)
        => values.TryGetValue(key, out var value) && !string.IsNullOrWhiteSpace(value)
            ? value
            : throw new ArgumentException($"{key} is required.");
}

static class Targets
{
    public static readonly Dictionary<uint, string> Apps = new()
    {
        [4165870] = "Steam Controller",
        [4165890] = "Steam Frame",
        [4165910] = "Steam Machine",
    };

    public static readonly Dictionary<uint, string> Packages = new()
    {
        [1558609] = "Steam Controller",
        [1629446] = "Steam Machine",
        [1629447] = "Steam Machine",
        [1629458] = "Steam Machine",
        [1629460] = "Steam Machine",
        [1629484] = "Steam Frame",
        [1629486] = "Steam Frame",
    };
}

static class PicsClient
{
    public static async Task<PicsSnapshot> FetchAsync(
        string username,
        string? password,
        string? accessToken,
        string? authCode,
        string? twoFactorCode,
        CancellationToken cancellationToken)
    {
        var steamClient = new SteamClient();
        var manager = new CallbackManager(steamClient);
        var steamUser = steamClient.GetHandler<SteamUser>() ?? throw new InvalidOperationException("SteamUser handler unavailable.");
        var steamApps = steamClient.GetHandler<SteamApps>() ?? throw new InvalidOperationException("SteamApps handler unavailable.");
        var login = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var disconnected = new TaskCompletionSource<string>(TaskCreationOptions.RunContinuationsAsynchronously);

        manager.Subscribe<SteamClient.ConnectedCallback>(_ =>
        {
            steamUser.LogOn(new SteamUser.LogOnDetails
            {
                Username = username,
                Password = password,
                AccessToken = accessToken,
                AuthCode = authCode,
                TwoFactorCode = twoFactorCode,
                ShouldRememberPassword = false,
            });
        });

        manager.Subscribe<SteamUser.LoggedOnCallback>(callback =>
        {
            if (callback.Result == EResult.OK)
            {
                login.TrySetResult();
                return;
            }

            var extra = callback.ExtendedResult == EResult.Invalid
                ? ""
                : $" extended={callback.ExtendedResult}";
            login.TrySetException(new InvalidOperationException(
                $"Steam logon failed: {callback.Result}{extra}. If Steam Guard is required, set STEAMKIT_AUTH_CODE or STEAMKIT_TWO_FACTOR_CODE."
            ));
        });

        manager.Subscribe<SteamClient.DisconnectedCallback>(callback =>
        {
            if (!callback.UserInitiated)
            {
                disconnected.TrySetResult("Steam disconnected before the PICS request completed.");
            }
        });

        steamClient.Connect();
        await PumpUntilAsync(manager, login.Task, disconnected.Task, cancellationToken);

        var aggregate = new ProductAggregate();
        var productInfo = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var appRequests = Targets.Apps.Keys.Select(id => new SteamApps.PICSRequest(id, 0)).ToList();
        var packageRequests = Targets.Packages.Keys.Select(id => new SteamApps.PICSRequest(id, 0)).ToList();
        var jobId = steamApps.PICSGetProductInfo(appRequests, packageRequests, metaDataOnly: false);

        using var subscription = manager.Subscribe<SteamApps.PICSProductInfoCallback>(jobId, callback =>
        {
            aggregate.Add(callback);
            if (!callback.ResponsePending)
            {
                productInfo.TrySetResult();
            }
        });

        await PumpUntilAsync(manager, productInfo.Task, disconnected.Task, cancellationToken);

        steamUser.LogOff();
        steamClient.Disconnect();

        return aggregate.ToSnapshot();
    }

    static async Task PumpUntilAsync(
        CallbackManager manager,
        Task primary,
        Task<string> disconnected,
        CancellationToken cancellationToken)
    {
        while (!primary.IsCompleted)
        {
            if (disconnected.IsCompleted)
            {
                throw new InvalidOperationException(await disconnected);
            }

            await manager.RunWaitCallbackAsync(cancellationToken);
        }

        await primary;
    }
}

sealed class ProductAggregate
{
    readonly Dictionary<uint, SteamApps.PICSProductInfoCallback.PICSProductInfo> apps = new();
    readonly Dictionary<uint, SteamApps.PICSProductInfoCallback.PICSProductInfo> packages = new();
    readonly HashSet<uint> unknownApps = new();
    readonly HashSet<uint> unknownPackages = new();

    public void Add(SteamApps.PICSProductInfoCallback callback)
    {
        foreach (var pair in callback.Apps)
        {
            apps[pair.Key] = pair.Value;
        }

        foreach (var pair in callback.Packages)
        {
            packages[pair.Key] = pair.Value;
        }

        foreach (var app in callback.UnknownApps)
        {
            unknownApps.Add(app);
        }

        foreach (var package in callback.UnknownPackages)
        {
            unknownPackages.Add(package);
        }
    }

    public PicsSnapshot ToSnapshot()
    {
        return new PicsSnapshot(
            DateTimeOffset.UtcNow,
            apps.ToDictionary(pair => pair.Key.ToString(), pair => ProductInfo.From(pair.Value)),
            packages.ToDictionary(pair => pair.Key.ToString(), pair => ProductInfo.From(pair.Value)),
            unknownApps.Order().ToArray(),
            unknownPackages.Order().ToArray()
        );
    }
}

sealed record PicsSnapshot(
    DateTimeOffset FetchedAtUtc,
    Dictionary<string, ProductInfo> Apps,
    Dictionary<string, ProductInfo> Packages,
    uint[] UnknownApps,
    uint[] UnknownPackages
);

sealed record ProductInfo(
    uint Id,
    uint ChangeNumber,
    bool MissingToken,
    bool OnlyPublic,
    bool UseHttp,
    string? HttpUri,
    string? ShaHash,
    KeyValueNode? KeyValues)
{
    public static ProductInfo From(SteamApps.PICSProductInfoCallback.PICSProductInfo info)
        => new(
            info.ID,
            info.ChangeNumber,
            info.MissingToken,
            info.OnlyPublic,
            info.UseHttp,
            info.HttpUri?.ToString(),
            info.SHAHash is null ? null : Convert.ToHexString(info.SHAHash),
            info.KeyValues is null ? null : KeyValueNode.From(info.KeyValues)
        );
}

sealed record KeyValueNode(string Name, string? Value, List<KeyValueNode> Children)
{
    public static KeyValueNode From(KeyValue keyValue)
        => new(
            keyValue.Name ?? "",
            keyValue.Value,
            keyValue.Children.Select(From).ToList()
        );

    public KeyValueNode? Child(string name)
        => Children.FirstOrDefault(child => string.Equals(child.Name, name, StringComparison.OrdinalIgnoreCase));

    public string? Path(params string[] names)
    {
        var current = this;
        foreach (var name in names)
        {
            current = current.Child(name);
            if (current is null)
            {
                return null;
            }
        }

        return current.Value;
    }
}

static class ReportRows
{
    public static List<string[]> Build(PicsSnapshot snapshot)
    {
        var rows = new List<string[]>
        {
            new[] { "type", "product", "id", "status", "changenumber", "related_ids", "details" },
        };

        foreach (var (id, product) in Targets.Apps.OrderBy(pair => pair.Key))
        {
            var key = id.ToString();
            rows.Add(snapshot.Apps.TryGetValue(key, out var info)
                ? AppRow(product, info)
                : MissingRow("app", product, id, snapshot.UnknownApps.Contains(id) ? "unknown" : "missing"));
        }

        foreach (var (id, product) in Targets.Packages.OrderBy(pair => pair.Key))
        {
            var key = id.ToString();
            rows.Add(snapshot.Packages.TryGetValue(key, out var info)
                ? PackageRow(product, info)
                : MissingRow("package", product, id, snapshot.UnknownPackages.Contains(id) ? "unknown" : "missing"));
        }

        return rows;
    }

    static string[] AppRow(string product, ProductInfo info)
    {
        var name = info.KeyValues?.Path("common", "name") ?? "";
        var depotIds = info.KeyValues?.Child("depots")?.Children
            .Where(child => uint.TryParse(child.Name, out _))
            .Select(child => child.Name)
            .Order()
            .ToArray() ?? Array.Empty<string>();
        var branchCount = info.KeyValues?.Child("depots")?.Child("branches")?.Children.Count ?? 0;
        var status = info.MissingToken ? "missing_token" : "available";
        var details = $"name={name}; depots={depotIds.Length}; branches={branchCount}; only_public={info.OnlyPublic}";

        return new[]
        {
            "app",
            product,
            info.Id.ToString(),
            status,
            info.ChangeNumber.ToString(),
            string.Join(",", depotIds),
            details,
        };
    }

    static string[] PackageRow(string product, ProductInfo info)
    {
        var appIds = info.KeyValues?.Child("appids")?.Children
            .Select(child => child.Name)
            .Where(name => uint.TryParse(name, out _))
            .Order()
            .ToArray() ?? Array.Empty<string>();
        var status = info.MissingToken ? "missing_token" : "available";
        var details = $"apps={string.Join(",", appIds)}; only_public={info.OnlyPublic}";

        return new[]
        {
            "package",
            product,
            info.Id.ToString(),
            status,
            info.ChangeNumber.ToString(),
            string.Join(",", appIds),
            details,
        };
    }

    static string[] MissingRow(string type, string product, uint id, string status)
        => new[] { type, product, id.ToString(), status, "", "", "PICS product info was not returned" };
}
