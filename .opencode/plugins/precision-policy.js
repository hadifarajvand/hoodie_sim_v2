/**
 * Precision Policy Plugin
 *
 * Conservative local policy hooks for OpenCode.
 * This intentionally avoids external dependencies.
 */
export const PrecisionPolicyPlugin = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && typeof output?.args?.filePath === "string") {
        const filePath = output.args.filePath
        if (
          filePath.includes(".env") ||
          filePath.includes("id_rsa") ||
          filePath.includes("id_ed25519") ||
          filePath.includes(".pem") ||
          filePath.includes(".key") ||
          filePath.includes(".crt") ||
          filePath.includes(".p12") ||
          filePath.includes(".pfx")
        ) {
          throw new Error("Blocked by precision-policy: secret-like file access is not allowed")
        }
      }

      if (input.tool === "bash" && typeof output?.args?.command === "string") {
        const command = output.args.command
        if (
          command.includes("rm -rf") ||
          command.includes("git reset --hard") ||
          command.includes("git clean -fd") ||
          command.includes("deploy") ||
          command.includes("kubectl delete") ||
          command.includes("terraform destroy")
        ) {
          throw new Error("Blocked by precision-policy: destructive shell command is not allowed")
        }
      }
    },
    event: async ({ event }) => {
      if (event?.type === "session.idle") {
        // No-op placeholder for future learned-session state handling.
      }
    }
  }
}
