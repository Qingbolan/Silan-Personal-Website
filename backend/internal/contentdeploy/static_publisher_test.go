package contentdeploy

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestCommandStaticPublisherReturnsVerifiedReleaseID(t *testing.T) {
	command := writePublisherCommand(t, `
echo "build output"
echo "[frontend:server] release=/srv/releases/20260726T120000Z-42"
`)
	release, err := NewCommandStaticPublisher(command).Publish(context.Background(), ReleaseContext{})
	if err != nil {
		t.Fatal(err)
	}
	if release != "20260726T120000Z-42" {
		t.Fatalf("release = %q", release)
	}
}

func TestCommandStaticPublisherRequiresReleaseMarker(t *testing.T) {
	command := writePublisherCommand(t, `echo "build completed without promotion"`)
	_, err := NewCommandStaticPublisher(command).Publish(context.Background(), ReleaseContext{})
	if err == nil || !strings.Contains(err.Error(), "verified release marker") {
		t.Fatalf("error = %v", err)
	}
}

func TestCommandStaticPublisherBindsReleaseProvenanceToEnvironment(t *testing.T) {
	command := writePublisherCommand(t, `
test "$SILAN_CONTENT_COMMIT" = "commit-42"
test "$SILAN_CONTENT_HASH" = "hash-42"
test "$SILAN_SCHEMA_VERSION" = "7"
echo "[frontend:server] release=/srv/releases/release-42"
`)
	release, err := NewCommandStaticPublisher(command).Publish(context.Background(), ReleaseContext{
		ContentCommit: "commit-42",
		ContentHash:   "hash-42",
		SchemaVersion: 7,
	})
	if err != nil {
		t.Fatal(err)
	}
	if release != "release-42" {
		t.Fatalf("release = %q", release)
	}
}

func writePublisherCommand(t *testing.T, body string) string {
	t.Helper()
	path := filepath.Join(t.TempDir(), "publish")
	script := "#!/bin/sh\nset -eu\n" + body + "\n"
	if err := os.WriteFile(path, []byte(script), 0o755); err != nil {
		t.Fatal(err)
	}
	return path
}
