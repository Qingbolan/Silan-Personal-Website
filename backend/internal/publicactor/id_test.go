package publicactor

import (
	"strings"
	"testing"
)

func TestIDIsStableScopedAndNonRevealing(t *testing.T) {
	const privateKey = "private-browser-fingerprint"
	visitor := ID(Visitor, privateKey)
	if visitor != ID(Visitor, privateKey) {
		t.Fatal("public actor ID must be stable")
	}
	if visitor == ID(User, privateKey) {
		t.Fatal("user and visitor namespaces must not collide")
	}
	if strings.Contains(visitor, privateKey) {
		t.Fatal("public actor ID exposed its private source")
	}
	if kind, ok := KindOf(visitor); !ok || kind != Visitor {
		t.Fatalf("KindOf(%q) = %q, %v", visitor, kind, ok)
	}
}
