// Package publicactor projects private runtime identities onto stable,
// non-reversible identifiers that are safe to place in public URLs.
package publicactor

import (
	"crypto/sha256"
	"encoding/base32"
	"strings"
)

type Kind string

const (
	User    Kind = "user"
	Visitor Kind = "visitor"
)

const actorIDSalt = "silan-public-actor:v1:"

// ID returns a deterministic public handle without exposing an OAuth identity
// ID or browser fingerprint. Empty private keys never produce a route.
func ID(kind Kind, privateKey string) string {
	privateKey = strings.TrimSpace(privateKey)
	if privateKey == "" {
		return ""
	}
	sum := sha256.Sum256([]byte(actorIDSalt + string(kind) + ":" + privateKey))
	token := base32.StdEncoding.WithPadding(base32.NoPadding).EncodeToString(sum[:10])
	return string(kind) + "_" + strings.ToLower(token)
}

func KindOf(actorID string) (Kind, bool) {
	switch {
	case strings.HasPrefix(actorID, string(User)+"_"):
		return User, true
	case strings.HasPrefix(actorID, string(Visitor)+"_"):
		return Visitor, true
	default:
		return "", false
	}
}
