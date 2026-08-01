export function BrandMark({ size = 34 }: { size?: number }) {
  return (
    <img
      src="/logo.jpg"
      alt=""
      width={size}
      height={size}
      style={{ width: size, height: size, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }}
    />
  );
}
