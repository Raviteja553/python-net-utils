# Errors and exit codes

netutil reports failures as typed errors. Each error has a fixed exit code,
so a script can react to a failure without reading text.

## Error hierarchy

```
NetutilError                exit 1  base class, catch this for any netutil failure
├── InputFileError          exit 3  file missing, unreadable, a directory, or not UTF-8
├── ParseError              exit 4  file read fine, but no interfaces found
├── RecordValidationError   exit 5  a parsed record broke a rule (carries .problems)
└── DeviceUnreachableError  exit 6  reserved, not used yet (carries .host)
```

Wrong usage (missing `--input`, no command) exits 2. argparse does this itself.

## Exit codes

| Code | Meaning | Error class |
|------|---------|-------------|
| 0 | success | none |
| 1 | generic netutil error | `NetutilError` |
| 2 | wrong usage | none (argparse) |
| 3 | input file problem | `InputFileError` |
| 4 | no interfaces found | `ParseError` |
| 5 | invalid record | `RecordValidationError` |
| 6 | device unreachable (reserved) | `DeviceUnreachableError` |

Earlier versions returned 2 for every bad input. Codes 3 to 5 replace that.

## Where output goes

- **stdout:** the result. On success, a JSON object of interfaces. On failure, one JSON error object.
- **stderr:** log lines, one JSON object per line.

This means `> out.json` captures clean JSON, and `2> err.jsonl` captures clean logs.

On Windows, the logged `path` shows backslashes (for example `tests\\data\\show_interfaces.txt`), because JSON escapes each backslash.

## The error object

On failure, stdout holds:

| Field | Meaning |
|-------|---------|
| `ok` | always `false` |
| `error` | the error class name |
| `exit_code` | the same number the process returns |
| `message` | short description |
| `problems` | list of strings, only for `RecordValidationError` |

## Examples

### Success (exit 0)

```
python -m netutil.cli parse --input tests/data/show_interfaces.txt
```

stdout is a JSON object keyed by interface name. A missing description is `null`.
stderr has one log line:

```
{"ts": "...", "level": "INFO", "logger": "__main__", "msg": "parsed interfaces", "count": 4, "path": "tests\\data\\show_interfaces.txt"}
```

### Missing file (exit 3)

```
python -m netutil.cli parse --input nope.txt
```

stdout:

```
{
  "ok": false,
  "error": "InputFileError",
  "exit_code": 3,
  "message": "cannot read nope.txt: No such file or directory"
}
```

### Wrong content (exit 4)

```
python -m netutil.cli parse --input other.txt
```

where `other.txt` contains `hello world`. stdout:

```
{
  "ok": false,
  "error": "ParseError",
  "exit_code": 4,
  "message": "no interfaces found in other.txt"
}
```

stderr also has a warning for the line it skipped: `Skipping unrecognised header line: hello world`.

### Invalid record (exit 5)

```
python -m netutil.cli parse --input bad_mtu.txt
```

where `bad_mtu.txt` has `MTU 0 bytes` on an interface. stdout:

```
{
  "ok": false,
  "error": "RecordValidationError",
  "exit_code": 5,
  "message": "1 validation problem(s)",
  "problems": [
    "GigabitEthernet0/1: mtu: Input should be greater than 0"
  ]
}
```

Each problem names the interface, the field and the rule that failed.
All problems are reported together, not just the first.

### Wrong usage (exit 2)

```
python -m netutil.cli parse
```

```
usage: net-utils parse [-h] --input INPUT [--format {json}]
net-utils parse: error: the following arguments are required: --input
```

## Using it from a script

```
python -m netutil.cli parse --input "$FILE" > out.json
case $? in
  0) echo "ok" ;;
  3) echo "cannot read $FILE" ;;
  4) echo "not show interfaces output" ;;
  5) echo "records invalid, see out.json" ;;
  *) echo "other failure" ;;
esac
```

## Adding a new error

1. Subclass `NetutilError` in `src/netutil/errors.py`.
2. Set a unique `exit_code`.
3. Raise it where the failure happens, and add a test for the code.

## Limits

- `validate_sample.py` and `interface_status_report.py` still do their own file handling and use their own exit codes. They have not been moved onto the new errors yet.
- `DeviceUnreachableError` exists but nothing raises it yet.
