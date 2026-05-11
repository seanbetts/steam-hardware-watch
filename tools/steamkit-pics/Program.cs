using System.Text.Json;
using System.Text.Json.Serialization;
using SteamKit2;
using SteamKit2.Authentication;
using SteamKit2.Internal;

var options = Args.Parse(args);
var username = Env("STEAMKIT_USERNAME");
var password = Env("STEAMKIT_PASSWORD");
var accessToken = Env("STEAMKIT_ACCESS_TOKEN");
var authCode = Env("STEAMKIT_AUTH_CODE");
var twoFactorCode = Env("STEAMKIT_TWO_FACTOR_CODE");
var acceptMobileConfirmation = Env("STEAMKIT_ACCEPT_MOBILE_CONFIRMATION") == "1";
var timeoutSeconds = int.TryParse(Env("STEAMKIT_TIMEOUT_SECONDS"), out var parsedTimeout)
    ? parsedTimeout
    : 90;

using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(timeoutSeconds));
var jsonOptions = new JsonSerializerOptions
{
    WriteIndented = true,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
};

if (!string.IsNullOrWhiteSpace(options.AuthSessionOutPath))
{
    if (string.IsNullOrWhiteSpace(username) || string.IsNullOrWhiteSpace(password))
    {
        throw new InvalidOperationException("STEAMKIT_USERNAME and STEAMKIT_PASSWORD are required for auth bootstrap.");
    }

    var existingSession = SteamKitSession.Load(options.SessionFilePath);
    var session = await AuthClient.CreateSessionAsync(
        username,
        password,
        authCode,
        twoFactorCode,
        acceptMobileConfirmation,
        existingSession?.GuardData,
        cts.Token
    );
    Directory.CreateDirectory(Path.GetDirectoryName(options.AuthSessionOutPath) ?? ".");
    await File.WriteAllTextAsync(options.AuthSessionOutPath, JsonSerializer.Serialize(session, jsonOptions) + Environment.NewLine, cts.Token);
    return;
}

options.RequireWatchMode();
Directory.CreateDirectory(options.OutDir!);
Directory.CreateDirectory(Path.GetDirectoryName(options.ReportPath!) ?? ".");
Directory.CreateDirectory(Path.GetDirectoryName(options.KeyLinesPath!) ?? ".");
Directory.CreateDirectory(Path.GetDirectoryName(options.MarkdownReportPath!) ?? ".");

var savedSession = SteamKitSession.Load(options.SessionFilePath);
if (savedSession is not null)
{
    username = savedSession.Username;
    password = null;
    accessToken = savedSession.RefreshToken;
    authCode = null;
    twoFactorCode = null;
}

if (string.IsNullOrWhiteSpace(username) || (string.IsNullOrWhiteSpace(password) && string.IsNullOrWhiteSpace(accessToken)))
{
    throw new InvalidOperationException("STEAMKIT_USERNAME and STEAMKIT_PASSWORD, STEAMKIT_ACCESS_TOKEN, or a valid --session-file are required.");
}

var snapshot = await PicsClient.FetchAsync(username, password, accessToken, authCode, twoFactorCode, cts.Token);

await File.WriteAllTextAsync(
    Path.Combine(options.OutDir!, "pics-product-info.json"),
    JsonSerializer.Serialize(snapshot, jsonOptions) + Environment.NewLine,
    cts.Token
);

var previous = PreviousRows.Load(options.PreviousReportPath);
var rows = ReportRows.Build(snapshot, previous);
await File.WriteAllLinesAsync(
    options.ReportPath!,
    new[] { ReportRow.HeaderLine() }.Concat(rows.Select(row => row.ToTsv())),
    cts.Token
);

var keyLines = new List<string> { "SteamKit/PICS package snapshot:" };
keyLines.Add(ReportRow.HeaderLine());
keyLines.AddRange(rows.Take(40).Select(row => row.ToTsv()));
await File.WriteAllLinesAsync(options.KeyLinesPath!, keyLines, cts.Token);

await File.WriteAllTextAsync(options.MarkdownReportPath!, MarkdownReport.Build(snapshot, rows, options.PreviousReportPath), cts.Token);

static string? Env(string name) => Environment.GetEnvironmentVariable(name);

sealed record Args(
    string? OutDir,
    string? ReportPath,
    string? KeyLinesPath,
    string? MarkdownReportPath,
    string? PreviousReportPath,
    string? SessionFilePath,
    string? AuthSessionOutPath)
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
            Optional(values, "--out-dir"),
            Optional(values, "--report"),
            Optional(values, "--key-lines"),
            Optional(values, "--markdown-report"),
            values.TryGetValue("--previous-report", out var previousReport) && !string.IsNullOrWhiteSpace(previousReport)
                ? previousReport
                : null,
            Optional(values, "--session-file"),
            Optional(values, "--auth-session-out")
        );
    }

    public void RequireWatchMode()
    {
        _ = Require(OutDir, "--out-dir");
        _ = Require(ReportPath, "--report");
        _ = Require(KeyLinesPath, "--key-lines");
        _ = Require(MarkdownReportPath, "--markdown-report");
    }

    static string? Optional(Dictionary<string, string> values, string key)
        => values.TryGetValue(key, out var value) && !string.IsNullOrWhiteSpace(value)
            ? value
            : null;

    static string Require(string? value, string key)
        => !string.IsNullOrWhiteSpace(value) ? value : throw new ArgumentException($"{key} is required.");
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

sealed record SteamKitSession(
    [property: JsonPropertyName("username")] string Username,
    [property: JsonPropertyName("steam_id")] string? SteamId,
    [property: JsonPropertyName("refresh_token")] string RefreshToken,
    [property: JsonPropertyName("access_token")] string? AccessToken,
    [property: JsonPropertyName("guard_data")] string? GuardData,
    [property: JsonPropertyName("created_at_utc")] DateTimeOffset CreatedAtUtc)
{
    public static SteamKitSession? Load(string? path)
    {
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
        {
            return null;
        }

        var session = JsonSerializer.Deserialize<SteamKitSession>(File.ReadAllText(path));
        return string.IsNullOrWhiteSpace(session?.RefreshToken) ? null : session;
    }
}

static class AuthClient
{
    public static async Task<SteamKitSession> CreateSessionAsync(
        string username,
        string password,
        string? emailCode,
        string? deviceCode,
        bool acceptMobileConfirmation,
        string? guardData,
        CancellationToken cancellationToken)
    {
        var steamClient = new SteamClient();
        var manager = new CallbackManager(steamClient);
        var connected = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var disconnected = new TaskCompletionSource<string>(TaskCreationOptions.RunContinuationsAsynchronously);

        manager.Subscribe<SteamClient.ConnectedCallback>(_ => connected.TrySetResult());
        manager.Subscribe<SteamClient.DisconnectedCallback>(callback =>
        {
            if (!callback.UserInitiated)
            {
                disconnected.TrySetResult("Steam disconnected before auth completed.");
            }
        });

        steamClient.Connect();
        await CallbackPump.UntilAsync(manager, connected.Task, disconnected.Task, cancellationToken);

        var authTask = steamClient.Authentication.BeginAuthSessionViaCredentialsAsync(new AuthSessionDetails
        {
            Username = username,
            Password = password,
            DeviceFriendlyName = "steam-hardware-watch",
            PlatformType = EAuthTokenPlatformType.k_EAuthTokenPlatformType_SteamClient,
            WebsiteID = "Client",
            IsPersistentSession = true,
            GuardData = guardData,
            Authenticator = new EnvAuthenticator(emailCode, deviceCode, acceptMobileConfirmation),
        });

        await CallbackPump.UntilAsync(manager, authTask, disconnected.Task, cancellationToken);
        var authSession = await authTask;
        var pollTask = authSession.PollingWaitForResultAsync(cancellationToken);
        await CallbackPump.UntilAsync(manager, pollTask, disconnected.Task, cancellationToken);
        var result = await pollTask;

        steamClient.Disconnect();

        if (string.IsNullOrWhiteSpace(result.RefreshToken))
        {
            throw new InvalidOperationException("Steam auth completed without a refresh token.");
        }

        return new SteamKitSession(
            result.AccountName,
            authSession is CredentialsAuthSession credentials ? credentials.SteamID.ToString() : null,
            result.RefreshToken,
            result.AccessToken,
            result.NewGuardData,
            DateTimeOffset.UtcNow
        );
    }
}

sealed class EnvAuthenticator(string? emailCode, string? deviceCode, bool acceptMobileConfirmation) : IAuthenticator
{
    public Task<string> GetDeviceCodeAsync(bool previousCodeWasIncorrect)
    {
        if (!string.IsNullOrWhiteSpace(deviceCode) && !previousCodeWasIncorrect)
        {
            return Task.FromResult(deviceCode);
        }

        throw new InvalidOperationException("Steam mobile authenticator code required. Set STEAMKIT_TWO_FACTOR_CODE and rerun scripts/steamkit_auth.sh.");
    }

    public Task<string> GetEmailCodeAsync(string email, bool previousCodeWasIncorrect)
    {
        if (!string.IsNullOrWhiteSpace(emailCode) && !previousCodeWasIncorrect)
        {
            return Task.FromResult(emailCode);
        }

        throw new InvalidOperationException($"Steam Guard email code required for {email}. Set STEAMKIT_AUTH_CODE and rerun scripts/steamkit_auth.sh.");
    }

    public Task<bool> AcceptDeviceConfirmationAsync() => Task.FromResult(acceptMobileConfirmation);
}

static class CallbackPump
{
    public static async Task UntilAsync(
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
                ShouldRememberPassword = !string.IsNullOrWhiteSpace(accessToken),
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
        await CallbackPump.UntilAsync(manager, login.Task, disconnected.Task, cancellationToken);

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

        await CallbackPump.UntilAsync(manager, productInfo.Task, disconnected.Task, cancellationToken);

        steamUser.LogOff();
        steamClient.Disconnect();

        return aggregate.ToSnapshot();
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

sealed record PreviousRow(string ChangeNumber);

static class PreviousRows
{
    public static Dictionary<string, PreviousRow> Load(string? path)
    {
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
        {
            return new Dictionary<string, PreviousRow>(StringComparer.Ordinal);
        }

        var lines = File.ReadAllLines(path);
        if (lines.Length == 0)
        {
            return new Dictionary<string, PreviousRow>(StringComparer.Ordinal);
        }

        var header = lines[0].Split('\t');
        var typeIndex = Array.IndexOf(header, "type");
        var idIndex = Array.IndexOf(header, "id");
        var changeIndex = Array.IndexOf(header, "changenumber");
        if (typeIndex < 0 || idIndex < 0 || changeIndex < 0)
        {
            return new Dictionary<string, PreviousRow>(StringComparer.Ordinal);
        }

        var result = new Dictionary<string, PreviousRow>(StringComparer.Ordinal);
        foreach (var line in lines.Skip(1))
        {
            if (string.IsNullOrWhiteSpace(line))
            {
                continue;
            }

            var parts = line.Split('\t');
            if (parts.Length <= Math.Max(typeIndex, Math.Max(idIndex, changeIndex)))
            {
                continue;
            }

            result[$"{parts[typeIndex]}:{parts[idIndex]}"] = new PreviousRow(parts[changeIndex]);
        }

        return result;
    }
}

sealed record ReportRow(
    string Type,
    string Product,
    string Id,
    string Status,
    string ChangeNumber,
    string PreviousChangeNumber,
    string ChangedSincePrevious,
    string ShaHash,
    string OnlyPublic,
    string Name,
    string RelatedIds,
    string Details)
{
    public static string HeaderLine()
        => string.Join('\t', new[]
        {
            "type",
            "product",
            "id",
            "status",
            "changenumber",
            "previous_changenumber",
            "changed_since_previous",
            "sha_hash",
            "only_public",
            "name",
            "related_ids",
            "details",
        });

    public string ToTsv()
        => string.Join('\t', new[]
        {
            Type,
            Product,
            Id,
            Status,
            ChangeNumber,
            PreviousChangeNumber,
            ChangedSincePrevious,
            ShaHash,
            OnlyPublic,
            Name,
            RelatedIds,
            Details,
        }.Select(Tsv.Clean));
}

static class Tsv
{
    public static string Clean(string? value) => (value ?? "").Replace('\t', ' ').Replace('\n', ' ').Trim();
}

static class ReportRows
{
    public static List<ReportRow> Build(PicsSnapshot snapshot, Dictionary<string, PreviousRow> previous)
    {
        var rows = new List<ReportRow>();
        foreach (var (id, product) in Targets.Apps.OrderBy(pair => pair.Key))
        {
            var key = id.ToString();
            rows.Add(snapshot.Apps.TryGetValue(key, out var info)
                ? AppRow(product, info, previous)
                : MissingRow("app", product, id, snapshot.UnknownApps.Contains(id) ? "unknown" : "missing", previous));
        }

        foreach (var (id, product) in Targets.Packages.OrderBy(pair => pair.Key))
        {
            var key = id.ToString();
            rows.Add(snapshot.Packages.TryGetValue(key, out var info)
                ? PackageRow(product, info, previous)
                : MissingRow("package", product, id, snapshot.UnknownPackages.Contains(id) ? "unknown" : "missing", previous));
        }

        return rows;
    }

    static ReportRow AppRow(string product, ProductInfo info, Dictionary<string, PreviousRow> previous)
    {
        var name = info.KeyValues?.Path("common", "name") ?? "";
        var depotIds = info.KeyValues?.Child("depots")?.Children
            .Where(child => uint.TryParse(child.Name, out _))
            .Select(child => child.Name)
            .Order()
            .ToArray() ?? Array.Empty<string>();
        var branches = info.KeyValues?.Child("depots")?.Child("branches")?.Children ?? new List<KeyValueNode>();
        var branchNames = branches.Select(branch => branch.Name).Where(name => !string.IsNullOrWhiteSpace(name)).Order().ToArray();
        var branchBuildIds = branches
            .Select(branch => (branch.Name, BuildId: branch.Path("buildid")))
            .Where(branch => !string.IsNullOrWhiteSpace(branch.Name) && !string.IsNullOrWhiteSpace(branch.BuildId))
            .Select(branch => $"{branch.Name}:{branch.BuildId}")
            .Order()
            .ToArray();
        var status = info.MissingToken ? "private_metadata_token_required" : "available";
        var details = $"depots_count={depotIds.Length}; branch_names={string.Join(",", branchNames)}; branch_buildids={string.Join(",", branchBuildIds)}";

        return WithPrevious(
            "app",
            product,
            info.Id.ToString(),
            status,
            info.ChangeNumber.ToString(),
            info.ShaHash ?? "",
            info.OnlyPublic.ToString(),
            name,
            string.Join(",", depotIds),
            details,
            previous
        );
    }

    static ReportRow PackageRow(string product, ProductInfo info, Dictionary<string, PreviousRow> previous)
    {
        var appIds = info.KeyValues?.Child("appids")?.Children
            .Select(child => child.Name)
            .Where(name => uint.TryParse(name, out _))
            .Order()
            .ToArray() ?? Array.Empty<string>();
        var name = info.KeyValues?.Path("name") ?? info.KeyValues?.Path("common", "name") ?? "";
        var status = info.MissingToken ? "private_metadata_token_required" : "available";
        var details = $"apps_count={appIds.Length}";

        return WithPrevious(
            "package",
            product,
            info.Id.ToString(),
            status,
            info.ChangeNumber.ToString(),
            info.ShaHash ?? "",
            info.OnlyPublic.ToString(),
            name,
            string.Join(",", appIds),
            details,
            previous
        );
    }

    static ReportRow MissingRow(string type, string product, uint id, string status, Dictionary<string, PreviousRow> previous)
        => WithPrevious(type, product, id.ToString(), status, "", "", "", "", "", "PICS product info was not returned", previous);

    static ReportRow WithPrevious(
        string type,
        string product,
        string id,
        string status,
        string changeNumber,
        string shaHash,
        string onlyPublic,
        string name,
        string relatedIds,
        string details,
        Dictionary<string, PreviousRow> previous)
    {
        previous.TryGetValue($"{type}:{id}", out var previousRow);
        var previousChange = previousRow?.ChangeNumber ?? "";
        var changed = "";
        if (!string.IsNullOrWhiteSpace(changeNumber))
        {
            changed = string.IsNullOrWhiteSpace(previousChange)
                ? "new"
                : previousChange == changeNumber ? "no" : "yes";
        }

        return new ReportRow(type, product, id, status, changeNumber, previousChange, changed, shaHash, onlyPublic, name, relatedIds, details);
    }
}

static class MarkdownReport
{
    public static string Build(PicsSnapshot snapshot, List<ReportRow> rows, string? previousReportPath)
    {
        var lines = new List<string>
        {
            "# SteamKit / PICS Detail",
            "",
            $"Fetched at UTC: `{snapshot.FetchedAtUtc:O}`",
            "",
            "SteamKit/PICS is the direct Steam metadata check. A `private_metadata_token_required` status means Steam returned the product shell and changenumber but withheld private product details without a PICS token. For this project, that is still useful as a movement signal, not a public-readiness signal.",
            "",
        };

        if (!string.IsNullOrWhiteSpace(previousReportPath))
        {
            lines.Add($"Previous report: `{previousReportPath}`");
            lines.Add("");
        }

        var changedRows = rows.Where(row => row.ChangedSincePrevious is "yes" or "new").ToList();
        lines.Add("## Changenumber Movement");
        lines.Add("");
        if (changedRows.Count == 0)
        {
            lines.Add("- No watched SteamKit/PICS changenumber movement versus the previous report.");
        }
        else
        {
            lines.AddRange(changedRows.Select(row =>
                $"- `{row.Type}` `{row.Product}` `{row.Id}`: `{row.PreviousChangeNumber}` -> `{row.ChangeNumber}` (`{row.Status}`)"
            ));
        }

        lines.Add("");
        lines.Add("## Watched Products");
        lines.Add("");
        foreach (var product in rows.Select(row => row.Product).Distinct().Order())
        {
            lines.Add($"### {product}");
            lines.Add("");
            foreach (var row in rows.Where(row => row.Product == product).OrderBy(row => row.Type).ThenBy(row => row.Id))
            {
                var interpretation = row.Status == "available"
                    ? "metadata available"
                    : row.Status == "private_metadata_token_required"
                        ? "movement signal only; private metadata is withheld"
                        : "unavailable in this run";
                lines.Add($"- `{row.Type}` `{row.Id}`: changenumber `{row.ChangeNumber}`, previous `{row.PreviousChangeNumber}`, changed `{row.ChangedSincePrevious}`, status `{row.Status}` ({interpretation}).");
                if (!string.IsNullOrWhiteSpace(row.Name))
                {
                    lines.Add($"  Name: `{row.Name}`.");
                }
                if (!string.IsNullOrWhiteSpace(row.RelatedIds))
                {
                    lines.Add($"  Related IDs: `{row.RelatedIds}`.");
                }
                if (!string.IsNullOrWhiteSpace(row.ShaHash))
                {
                    lines.Add($"  SHA hash: `{row.ShaHash}`.");
                }
                if (!string.IsNullOrWhiteSpace(row.Details))
                {
                    lines.Add($"  Details: `{row.Details}`.");
                }
            }

            lines.Add("");
        }

        lines.Add("## Raw Outputs");
        lines.Add("");
        lines.Add("- Raw JSON: `api/steamkit/pics-product-info.json`");
        lines.Add("- Compact TSV: `reports/steamkit-pics-packages.tsv`");
        lines.Add("");

        return string.Join(Environment.NewLine, lines);
    }
}
