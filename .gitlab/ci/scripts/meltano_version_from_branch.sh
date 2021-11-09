set -e

echo "Initializing meltano version number variables..."
export RELEASE_VERSION="${CI_COMMIT_REF_NAME#release/v}"
CODE_VERSION="$(bumpversion major --allow-dirty --dry-run --list | grep current_version= | cut -d'=' -f2)"
echo "Detected code version '$CODE_VERSION' and release version '$RELEASE_VERSION' (from git ref '$CI_COMMIT_REF_NAME')"
[[ "$CODE_VERSION" == "" ]] && echo "Could not detect current version" && exit 1
[[ "$RELEASE_VERSION" == "" ]] && echo "Could not detect new version" && exit 1
