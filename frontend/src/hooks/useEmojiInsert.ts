import { useRef } from "react";

export function useEmojiInsert<T extends HTMLTextAreaElement | HTMLInputElement>(
  value: string,
  setValue: (value: string) => void,
) {
  const ref = useRef<T>(null);

  const insertEmoji = (emoji: string) => {
    const element = ref.current;
    if (!element) {
      setValue(value + emoji);
      return;
    }

    const start = element.selectionStart ?? value.length;
    const end = element.selectionEnd ?? value.length;
    const next = value.slice(0, start) + emoji + value.slice(end);
    setValue(next);

    const cursor = start + emoji.length;
    requestAnimationFrame(() => {
      element.focus();
      element.setSelectionRange(cursor, cursor);
    });
  };

  return { ref, insertEmoji };
}
