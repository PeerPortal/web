import Image from 'next/image';

export default function Logo({ size = 120 }: { size?: number }) {
  return (
    <Image
      src="/icon.png"
      alt="OfferIn Logo"
      width={size}
      height={size}
      className="object-contain"
    />
  );
}
