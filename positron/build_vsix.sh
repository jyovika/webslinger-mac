#!/bin/sh
# Packs this folder into WebSlinger.vsix without needing Node's vsce tool.
set -e
cd "$(dirname "$0")"
python3 -c 'import json; json.load(open("package.json")); json.load(open("themes/webslinger-color-theme.json"))'
tmp=$(mktemp -d)
mkdir -p "$tmp/extension/themes"
cp package.json "$tmp/extension/"
cp themes/webslinger-color-theme.json "$tmp/extension/themes/"
cat > "$tmp/extension.vsixmanifest" <<'EOF'
<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="webslinger-theme" Version="1.0.0" Publisher="jyovika"/>
    <DisplayName>WebSlinger</DisplayName>
    <Description xml:space="preserve">Dark red-and-black theme matching the WebSlinger RStudio theme</Description>
    <Categories>Themes</Categories>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.80.0"/>
    </Properties>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
  </Assets>
</PackageManifest>
EOF
cat > "$tmp/[Content_Types].xml" <<'EOF'
<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
</Types>
EOF
rm -f WebSlinger.vsix
(cd "$tmp" && zip -qr "$OLDPWD/WebSlinger.vsix" "[Content_Types].xml" extension.vsixmanifest extension)
rm -rf "$tmp"
echo "Built $(pwd)/WebSlinger.vsix"
