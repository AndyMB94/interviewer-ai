import { Smile } from "lucide-react";
import EmojiPicker, { Theme, type EmojiClickData } from "emoji-picker-react";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useTheme } from "@/hooks/useTheme";

export function EmojiPickerButton({ onSelect }: { onSelect: (emoji: string) => void }) {
  const { theme } = useTheme();

  return (
    <Popover>
      <PopoverTrigger render={<Button type="button" variant="ghost" size="icon-sm" />}>
        <Smile />
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <EmojiPicker
          onEmojiClick={(data: EmojiClickData) => onSelect(data.emoji)}
          theme={theme === "dark" ? Theme.DARK : Theme.LIGHT}
          width={300}
          height={350}
        />
      </PopoverContent>
    </Popover>
  );
}
