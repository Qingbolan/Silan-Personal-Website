package contentdeploy

import (
	"context"
	"fmt"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

const staticPublishTimeout = 3 * time.Minute

// StaticPublisher materializes the crawler-visible frontend projection after
// a content transaction. Implementations must return only after the release is
// verified and live; a queued or fire-and-forget refresh is not a successful
// content deployment.
type StaticPublisher interface {
	Publish(context.Context) (string, error)
}

// CommandStaticPublisher runs the server-owned frontend release command. The
// executable is invoked directly rather than through a shell so configuration
// cannot inject additional commands.
type CommandStaticPublisher struct {
	executable string
}

func NewCommandStaticPublisher(executable string) StaticPublisher {
	executable = strings.TrimSpace(executable)
	if executable == "" {
		return nil
	}
	return &CommandStaticPublisher{executable: executable}
}

func (publisher *CommandStaticPublisher) Publish(ctx context.Context) (string, error) {
	if !filepath.IsAbs(publisher.executable) {
		return "", fmt.Errorf("static publisher must be an absolute executable path")
	}
	publishCtx, cancel := context.WithTimeout(ctx, staticPublishTimeout)
	defer cancel()

	output, err := exec.CommandContext(publishCtx, publisher.executable).CombinedOutput()
	if err != nil {
		if publishCtx.Err() != nil {
			return "", fmt.Errorf("static publisher timed out: %w", publishCtx.Err())
		}
		return "", fmt.Errorf(
			"static publisher failed: %w: %s",
			err,
			strings.TrimSpace(string(output)),
		)
	}
	const marker = "[frontend:server] release="
	lines := strings.Split(strings.TrimSpace(string(output)), "\n")
	for index := len(lines) - 1; index >= 0; index-- {
		line := strings.TrimSpace(lines[index])
		if value, found := strings.CutPrefix(line, marker); found {
			release := filepath.Base(strings.TrimSpace(value))
			if release != "." && release != "" {
				return release, nil
			}
		}
	}
	return "", fmt.Errorf("static publisher completed without a verified release marker")
}
