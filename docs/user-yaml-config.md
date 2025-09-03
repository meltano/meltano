# User YAML Configuration

Meltano allows users to customize YAML formatting preferences through a user configuration file.

## Configuration File

User preferences are stored in a platform-specific configuration directory using YAML format.

### Configuration File Location

The configuration file location follows platform conventions:

- **Linux**: `$XDG_CONFIG_HOME/meltano/config.yml` (typically `~/.config/meltano/config.yml`)
- **macOS**: `~/Library/Application Support/meltano/config.yml`
- **Windows**: `%APPDATA%\meltano\config.yml`

The location respects the `XDG_CONFIG_HOME` environment variable on Linux systems when set.

### Creating the Configuration File

The configuration directory and file are created automatically when Meltano first needs to read user configuration. You can also create them manually:

**Linux/macOS:**
```bash
# Create the directory
mkdir -p ~/.config/meltano  # Linux
mkdir -p "~/Library/Application Support/meltano"  # macOS

# Create the config file
touch ~/.config/meltano/config.yml  # Linux
touch "~/Library/Application Support/meltano/config.yml"  # macOS
```

### Configuration Format

```yaml
yaml:
  indent: 4
  block_seq_indent: 2
  sequence_dash_offset: 2
```

## Available Settings

### YAML Indentation Settings

- `indent` (int): Base indentation level for mappings (default: 2, minimum: 1)
- `block_seq_indent` (int): Additional indentation for block sequences (default: 0, minimum: 0)
- `sequence_dash_offset` (int): Offset for sequence dashes (default: max(0, indent-2), minimum: 0)

## Example Configurations

### Standard 2-space indentation (default)
```yaml
yaml:
  indent: 2
  block_seq_indent: 0
  sequence_dash_offset: 0
```

### 4-space indentation with block sequence indentation
```yaml
yaml:
  indent: 4
  block_seq_indent: 2
  sequence_dash_offset: 2
```

## How It Works

When Meltano writes YAML files (like `meltano.yml`), it applies these user configuration settings to control the formatting. The settings affect:

- **indent**: Controls how much mapping keys are indented from their parent
- **block_seq_indent**: Additional indentation for sequence items beyond the base indent
- **sequence_dash_offset**: How far sequence dashes (`-`) are offset from the left margin

### Invalid Values

If invalid values are provided, Meltano will log a warning and fall back to defaults:
- Negative `indent` values default to 2
- Negative `block_seq_indent` values default to 0

## Disabling User Configuration

Set the `MELTANO_DISABLE_USER_YAML_CONFIG` environment variable to any truthy value (`1`, `true`, `yes`, `on`) to disable user configuration:

```bash
export MELTANO_DISABLE_USER_YAML_CONFIG=true
```

This forces Meltano to use default YAML formatting settings.
