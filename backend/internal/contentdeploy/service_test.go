package contentdeploy

import (
	"archive/tar"
	"bytes"
	"compress/gzip"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

func TestExtractBundleRejectsPathTraversal(t *testing.T) {
	var compressed bytes.Buffer
	gz := gzip.NewWriter(&compressed)
	archive := tar.NewWriter(gz)
	data := []byte("unsafe")
	header := &tar.Header{Name: "../outside", Mode: 0o600, Size: int64(len(data))}
	if err := archive.WriteHeader(header); err != nil {
		t.Fatal(err)
	}
	if _, err := archive.Write(data); err != nil {
		t.Fatal(err)
	}
	if err := archive.Close(); err != nil {
		t.Fatal(err)
	}
	if err := gz.Close(); err != nil {
		t.Fatal(err)
	}
	if err := extractBundle(&compressed, t.TempDir(), 1024); err == nil {
		t.Fatal("expected unsafe archive path to be rejected")
	}
}

func TestValidateDatabaseBindsManifestToProjection(t *testing.T) {
	path := filepath.Join(t.TempDir(), "portfolio.db")
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := db.Exec(`CREATE TABLE sync_meta (
		content_hash TEXT NOT NULL,
		content_commit TEXT NOT NULL
	); INSERT INTO sync_meta VALUES ('hash-1', 'commit-1')`); err != nil {
		t.Fatal(err)
	}
	if err := db.Close(); err != nil {
		t.Fatal(err)
	}
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	sum := sha256.Sum256(data)
	manifest := &Manifest{
		Version:       BundleVersion,
		SchemaVersion: ProjectionSchemaVersion,
		ContentCommit: "commit-1",
		ContentHash:   "hash-1",
		DatabaseSHA:   hex.EncodeToString(sum[:]),
		Media:         []MediaAsset{},
	}
	if err := validateDatabase(path, manifest); err != nil {
		t.Fatalf("valid projection rejected: %v", err)
	}
	manifest.ContentCommit = "different"
	if err := validateDatabase(path, manifest); err == nil {
		t.Fatal("expected mismatched manifest to be rejected")
	}
}

func TestReconcileMediaDeletesObsoleteFilesAndValidatesGeneration(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "keep.png"), []byte("keep"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(root, "delete.png"), []byte("delete"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := reconcileMedia(root, map[string]string{"keep.png": fnvHash([]byte("keep"))}); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(filepath.Join(root, "delete.png")); !os.IsNotExist(err) {
		t.Fatalf("obsolete media still exists: %v", err)
	}
}

func TestReconcileMediaRequestsOnlyFilesWhoseHashDoesNotMatch(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "changed.png"), []byte("old"), 0o644); err != nil {
		t.Fatal(err)
	}
	err := reconcileMedia(root, map[string]string{
		"changed.png": fnvHash([]byte("new")),
		"missing.png": fnvHash([]byte("missing")),
	})
	var required *MediaRequiredError
	if !errors.As(err, &required) {
		t.Fatalf("error = %v, want MediaRequiredError", err)
	}
	if len(required.UploadPaths) != 2 ||
		required.UploadPaths[0] != "changed.png" ||
		required.UploadPaths[1] != "missing.png" {
		t.Fatalf("upload paths = %v", required.UploadPaths)
	}
}

func TestDeploymentLifecycleRejectsSkippedAndTerminalTransitions(t *testing.T) {
	lifecycle := newDeploymentLifecycle()
	if err := lifecycle.transition(StatePromoting); err == nil {
		t.Fatal("expected receiving -> promoting to be rejected")
	}
	for _, state := range []State{
		StateValidated,
		StatePromoting,
		StateVerifying,
		StateRendering,
		StateComplete,
	} {
		if err := lifecycle.transition(state); err != nil {
			t.Fatalf("transition to %s: %v", state, err)
		}
	}
	if err := lifecycle.transition(StateFailed); err == nil {
		t.Fatal("expected terminal complete state to reject failure transition")
	}
}

func TestReleaseArchiveKeepsACompleteRollbackGeneration(t *testing.T) {
	root := t.TempDir()
	database := filepath.Join(root, "projection.db")
	media := filepath.Join(root, "desired-media")
	if err := os.WriteFile(database, []byte("projection"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(media, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(media, "figure.png"), []byte("figure"), 0o644); err != nil {
		t.Fatal(err)
	}
	service := &Service{config: Config{StateRoot: filepath.Join(root, "releases")}}
	manifest := &Manifest{
		Version:       BundleVersion,
		SchemaVersion: ProjectionSchemaVersion,
		ContentCommit: "commit-1",
		ContentHash:   "hash-1",
		DatabaseSHA:   "sha-1",
		Media:         []MediaAsset{},
	}
	commit, abort, err := service.stageReleaseArchive(database, media, manifest)
	if err != nil {
		t.Fatal(err)
	}
	defer abort()
	if err := commit(); err != nil {
		t.Fatal(err)
	}
	archives, err := releaseArchivePaths(service.config.StateRoot)
	if err != nil {
		t.Fatal(err)
	}
	if len(archives) != 1 || filepath.Base(archives[0]) != "commit-1" {
		t.Fatalf("archives = %v", archives)
	}
	for _, relative := range []string{"complete", "manifest.json", "portfolio.db", "media/figure.png"} {
		if _, err := os.Stat(filepath.Join(archives[0], relative)); err != nil {
			t.Fatalf("archive missing %s: %v", relative, err)
		}
	}
}

func fnvHash(data []byte) string {
	var hash uint64 = 0xcbf29ce484222325
	for _, value := range data {
		hash ^= uint64(value)
		hash *= 0x100000001b3
	}
	return fmt.Sprintf("%016x", hash)
}
