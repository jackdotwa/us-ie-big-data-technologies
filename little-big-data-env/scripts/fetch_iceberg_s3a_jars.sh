#!/usr/bin/env bash
# Downloads the jars the lakehouse profile mounts into every Spark container: the Iceberg Spark
# runtime (Iceberg tables in Spark SQL) and Hadoop S3A with the AWS SDK (Spark reads and writes s3a://).
# Versions match Spark 3.5 (Scala 2.12, Hadoop 3.3.4). Each jar is checked against Maven Central's SHA-1.
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)/jars/lakehouse"
MAVEN="https://repo1.maven.org/maven2"
JARS=(
  "org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.6.1/iceberg-spark-runtime-3.5_2.12-1.6.1.jar"
  "org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar"
  "com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar"
)

# sha1sum is GNU coreutils; older macOS has only shasum.
SHA1=(sha1sum); command -v sha1sum >/dev/null || SHA1=(shasum -a 1)

mkdir -p "$DIR"
for path in "${JARS[@]}"; do
  name="$(basename "$path")"
  if [ -f "$DIR/$name" ]; then
    echo "[=] $name already present"
  else
    echo "[*] Downloading $name"
    curl -fSL --retry 3 -o "$DIR/$name.part" "$MAVEN/$path"
    mv "$DIR/$name.part" "$DIR/$name"
  fi
  expected="$(curl -fsSL "$MAVEN/$path.sha1" | cut -c1-40)"
  actual="$("${SHA1[@]}" "$DIR/$name" | cut -c1-40)"
  if [ "$expected" != "$actual" ]; then
    echo "[!] Checksum mismatch for $name (expected $expected, got $actual)"; rm -f "$DIR/$name"; exit 1
  fi
  echo "[+] $name verified"
done
