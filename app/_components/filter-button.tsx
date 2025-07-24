import { Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function FilterButton({
  showFilters,
  setShowFilters
}: {
  showFilters: boolean;
  setShowFilters: (showFilters: boolean) => void;
}) {
  return (
    <Button
      onClick={() => setShowFilters(!showFilters)}
      className="group"
      variant="ghost"
      size="icon"
    >
      <Filter className="text-muted-foreground/80" size={20} />
    </Button>
  );
}
