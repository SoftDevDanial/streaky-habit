// Applies { from, to } edits to a source text. Every `from` must occur exactly once. The edits are written
// with \n, and are converted to the file's own line ending (src/ is CRLF in this Windows working tree).
export function applyEdits(text, edits, label) {
  const eol = text.includes("\r\n") ? "\r\n" : "\n";
  const fit = (piece) => piece.replaceAll("\n", eol);
  let result = text;
  for (const { from, to } of edits) {
    const parts = result.split(fit(from));
    if (parts.length !== 2) {
      throw new Error(`mutant edit matched ${parts.length - 1} times in ${label}: ${JSON.stringify(from.slice(0, 80))}`);
    }
    result = parts.join(fit(to));
  }
  return result;
}
