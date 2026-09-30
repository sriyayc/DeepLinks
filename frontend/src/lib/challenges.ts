export type Challenge = {
  id: string;
  title?: string;
  category?: string;
  prompt: string;
  ciphertext?: string;
  hint?: string;
  toolUrl?: string;
  toolLabel?: string;
  cipherDetails?: string;
  challengeUrl?: string;
  challengeLabel?: string;
  downloadUrl?: string;
  answerHash?: string;
};

// Points for a solve and the cost of revealing the hint, by difficulty.
// Kept in sync with the backend (routes/challenges.py CHALLENGES).
export function challengeTier(c: Challenge): { label: string; points: number; hintCost: number } {
  const cat = (c.category ?? "").toLowerCase();
  if (cat.includes("hard")) return { label: "Hard", points: 200, hintCost: 50 };
  if (cat.includes("medium")) return { label: "Medium", points: 100, hintCost: 25 };
  return { label: "Easy", points: 50, hintCost: 10 }; // beginner / easy
}

// Browser-only checking hides plaintext answers, but is not tamper-proof grading.
export const challenges: Challenge[] = [
  {
    id: "rot13-intro",
    answerHash: "8e03d4c7a5909fc590a32023838419d82421d0cad5025990d524caf9c0ab569d",
    title: "A little rotation",
    category: "Crypto · Beginner",
    prompt: "Someone scrambled a flag by rotating the letters. Decode the message below and submit the original flag.",
    ciphertext: "ynlre8{pelcgb_vf_sha}",
    hint: "Try ROT13: each letter moves 13 places through the alphabet. Numbers and symbols stay the same. Open CyberChef, paste the message into Input, and copy the decoded flag from Output.",
    toolUrl: "https://gchq.github.io/CyberChef/#recipe=ROT13(true,true,false,13)",
  },
  {
    id: "parceltrack-idor",
    answerHash: "c107721d65dfe56d6a4730fbdc75279ed70e041b6d0350b8868642be14ef8745",
    title: "An invoice mix-up",
    category: "Web · Beginner",
    prompt: "ParcelTrack lets you look up invoices by ID. Start with the prefilled login and explore the invoice portal. Can you find the flag in the admin console?",
    challengeUrl: "https://layer8idorsite.vercel.app/",
    challengeLabel: "Open IDOR challenge ↗",
  },
  {
    id: "pocket-pad",
    title: "Pocket Pad",
    category: "Crypto · Easy",
    prompt: "A friend says they made a one-time pad, but their entire key is only one byte. They XORed that same byte with every byte of the flag and sent you the result as hexadecimal.",
    ciphertext: "010c14081f55165d0308320f14195e32065e141e320c1f5e32035d19321e5e0e1f5e1910",
    answerHash: "176507a8908e11470e65d9f9b87a372505c679c5fc1afa3e17887fd924d789f5",
  },
  {
    id: "streetlights",
    title: "Streetlights",
    category: "Forensics · Easy",
    prompt: "A photograph can carry more than just pixels. Download this image and find the hidden flag.",
    downloadUrl: "/challenges/streetlights.jpg",
    answerHash: "9f54dfc07454e416094c356395ad82021d9be3a69f5a6d33c80e2f9719a8647f",
  },
  {
    id: "runaway",
    title: "Runaway",
    category: "Crypto · Medium",
    prompt: "A message was intercepted from a self-proclaimed session insider. They claimed the key wasn't hidden, just heard. The encryption is familiar, but the language it speaks isn't standard. Find the right alphabet. Then listen for the key and decrypt the message.",
    ciphertext: "1tKW6#CrqCBewYrMwAK 1tmuwWHvEYt",
    cipherDetails: "Construct the alphabet by reading the track titles below in order, preserving case and spaces, and keeping only the first occurrence of each character. Then append unseen characters from Python's string.ascii_letters + string.digits + string.punctuation + a space, in that order. Use zero-based positions in this alphabet. Encryption adds the plaintext and repeating key positions modulo the alphabet length.\n\nTrack titles (in order): Donda Chant; Jail; God Breathed; Off the Grid; Hurricane; Praise God; Jonah; Ok Ok; Junya; Believe What I Say; 24; Remote Control; Moon; Heaven and Hell; Donda; Keep My Spirit Alive; Jesus Lord; New Again; Tell The Vision; Lord I Need You; Pure Souls; Come to Life; No Child Left Behind.",
    hint: "The album is Donda. The key is a lowercase track title heard early in the album. Use the cipher details for the exact alphabet order.",
    toolUrl: "https://en.wikipedia.org/wiki/Donda",
    toolLabel: "Album reference ↗",
    answerHash: "d0793d24edeeab929cfadd528bd1cbcdd5fcad3caa734fc251ff0b236eeec5e8",
  },
  {
    id: "behind-the-page",
    title: "Behind the Page",
    category: "Web · Beginner",
    prompt: "The page offers two tempting shortcuts, but appearances can be misleading. Explore the page and find the real flag.",
    challengeUrl: "/challenges/behind-the-page/index.html",
    answerHash: "6e977ff8c8f5b2d6c8fd9fb15f61d08fade032a9fae2e7db30b6e64547f5af76",
  },
  {
    id: "concert-leak",
    title: "Concert Leak",
    category: "Forensics · Easy",
    prompt: "Someone leaked a concert photo. There may be more in this file than a picture. Download the original image and recover the hidden flag.",
    downloadUrl: "/challenges/concert_leak.jpg",
    answerHash: "5da1ef5bb2683ac32de4cfd8c233e1fc6086cdf43a5eac97d921f06094554ae7",
  },
  {
    id: "encrypted-tea",
    title: "gang the tea is ENCRYPTED 💀",
    category: "Crypto · Easy",
    prompt: "ok so my friend sent the group chat the best tea of the semester and it's just... this??\n\nthey said they wrapped it in 2 layers bc \"the tea is too spicy for plain text\" 😭\nlayer one is a super common internet text-scramble.\nlayer two is an old-school cipher that needs a secret word, and they left us ONE clue:\n\n\"the secret word is what i call the whole chat, no cap\"\n\npls decode it before it leaks 🙏",
    ciphertext: "cmFsa3g4e21sXzNkX2loMzRnM2pfMHRfbTN9",
    answerHash: "22bbadfbb0f5f54cd935723d088f9b7f7b6bcd33918bdb525a50b04cae01634f",
  },
  {
    id: "lost-laptop",
    title: "Lost Laptop",
    category: "Forensics · Easy",
    prompt: "Someone left their laptop behind, and this photo is your only lead. Download the image, uncover the hidden clue, and follow it to find the owner's message and flag.",
    downloadUrl: "/challenges/lost_laptop.png",
    answerHash: "8397f14ba4c52de3836825e727c6841be165b3db2b16875fd490bb407f3b3e55",
  },
];

export async function checkChallengeAnswer(challenge: Challenge, submitted: string): Promise<boolean> {
  if (!challenge.answerHash) return false;
  const bytes = new TextEncoder().encode(submitted.trim());
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  const hash = Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
  return hash === challenge.answerHash;
}