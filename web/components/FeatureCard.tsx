type FeatureCardProps = {
  title: string;
  summary: string;
};

export function FeatureCard({ title, summary }: FeatureCardProps) {
  return (
    <article className="card">
      <h2>{title}</h2>
      <p>{summary}</p>
    </article>
  );
}
