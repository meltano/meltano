set -evx

echo "Initializing meltano version number variables..."
export RELEASE_VERSION="${CI_COMMIT_REF_NAME#release/v}"
[[ "$RELEASE_VERSION" == "" ]] && echo "Could not detect release version" && exit 1

set +e
CODE_VERSION="$(bumpversion major --allow-dirty --dry-run --list | grep current_version= | cut -d'=' -f2)"
[[ "$CODE_VERSION" == "" ]] && echo "Could not detect current code version (bumpversion may not be installed)."
echo "Detected code version '$CODE_VERSION' and release version '$RELEASE_VERSION' (from git ref '$CI_COMMIT_REF_NAME')"
