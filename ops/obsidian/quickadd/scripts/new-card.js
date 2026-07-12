/*
 * scribectl — QuickAdd user script: "New card + contract"
 *
 * A thin, button-triggered bridge to `scribectl new card`. It deliberately
 * does NOT re-implement the scaffold: the card + contract + awaiting_scope
 * wiring is tested engine behavior with exactly one implementation
 * (scribectl/cli.py cmd_new_card). Forking it into untested JS is how canon
 * machinery drifts, so this shells the real command and surfaces its output.
 *
 * The writer never meets a terminal — they press a QuickAdd button; the shell
 * runs under the hood. Inbox jots and new nodes are native QuickAdd (no shell);
 * only this one delegates, on purpose.
 *
 * Install: drop this in your vault, point QuickAdd's "New card + contract"
 * macro at it, and set the two options below. `scribectl` must be reachable
 * at the configured path (Obsidian's PATH often omits ~/.local/bin — give the
 * absolute path from `which scribectl`).
 */
module.exports = {
  entry: async (params, settings) => {
    const { quickAddApi, obsidian } = params;
    const { Notice } = obsidian;

    const name = (await quickAddApi.inputPrompt(
      "Card name (e.g. Scene 02-01 / Episode 2-01)"
    ) || "").trim();
    if (!name) {
      new Notice("scribectl: cancelled — no card name");
      return;
    }

    const bin = settings["scribectl path"] || "scribectl";
    const cwd = settings["Project directory"];
    if (!cwd) {
      new Notice("scribectl: set the 'Project directory' option on this script");
      return;
    }

    const { execFile } = require("child_process");
    execFile(bin, ["new", "card", name], { cwd }, (err, stdout, stderr) => {
      if (err) {
        new Notice("scribectl new card failed:\n" + (stderr || err.message), 10000);
        return;
      }
      // cmd_new_card prints two `created …` lines and the awaiting_scope note.
      new Notice(stdout.trim() || `created card + contract for ${name}`, 8000);
    });
  },
  settings: {
    name: "scribectl new card",
    author: "scribectl",
    options: {
      "scribectl path": {
        type: "text",
        defaultValue: "scribectl",
        placeholder: "/home/you/.local/bin/scribectl",
      },
      "Project directory": {
        type: "text",
        defaultValue: "",
        placeholder: "/media/Creative/30 Creative/Works/Fertile Flames",
      },
    },
  },
};
