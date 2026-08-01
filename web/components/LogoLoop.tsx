/** A persistent, always-looping corner widget shown on every page: the logo
 * orbits once, then sinks in slow motion into a net graphic before the loop
 * resets and repeats — pure CSS, no JS, so it needs no session gating. */
export function LogoLoop() {
  return (
    <div className="logo-loop" aria-hidden="true">
      <div className="logo-loop-net" />
      <img src="/logo.jpg" alt="" className="logo-loop-ball" />
    </div>
  );
}
