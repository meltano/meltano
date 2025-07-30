# User YAML Configuration

Meltano allows users to customize YAML formatting preferences through a user configuration file.

## Configuration File

User preferences are stored in `~/.meltanorc` using INI format:

```ini
[yaml]
indent = 4
preserve_quotes = true
width = 80
```

## Available Settings

### Indentation Settings

- `indent` (int): Mapping indentation (default: 2)
- `block_seq_indent` (int): Additional sequence indentation (default: 0)
- `sequence_dash_offset` (int): Dash offset for sequences (default: max(0, indent-2))

### Formatting Options

- `preserve_quotes` (bool): Preserve original quote style
- `default_style` (string): Default scalar style ('', '|', '>')
- `width` (int): Maximum line width
- `explicit_start` (bool): Add explicit document start (---)
- `explicit_end` (bool): Add explicit document end (...)
- `version` (string): YAML version (e.g., "1.2")
- `allow_unicode` (bool): Allow Unicode characters

### Type Representation

- `default_flow_style` (bool): Use flow style by default
- `canonical` (bool): Output in canonical form
- `allow_duplicate_keys` (bool): Allow duplicate mapping keys

## Example Configuration

```ini
[yaml]
indent = 4
preserve_quotes = true
width = 120
explicit_start = true
```

## Disabling User Configuration

Set the environment variable to any truthy value (`1`, `true`, `yes`, `on`) to disable user configuration:

```bash
export MELTANO_DISABLE_USER_YAML_CONFIG=true
# or
export MELTANO_DISABLE_USER_YAML_CONFIG=1
# or
export MELTANO_DISABLE_USER_YAML_CONFIG=yes
```

This forces Meltano to use default YAML formatting settings.
