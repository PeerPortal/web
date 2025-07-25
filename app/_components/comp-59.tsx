import { useId } from 'react';

import { Label } from '_components/ui/label';
import { Textarea } from '_components/ui/textarea';

export default function Component() {
  const id = useId();
  return (
    <div className="*:not-first:mt-2">
      <Label htmlFor={id}>Simple textarea</Label>
      <Textarea id={id} placeholder="Leave a comment" />
    </div>
  );
}
