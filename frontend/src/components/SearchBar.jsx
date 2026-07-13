import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";

export function SearchBar({ initial = {}, variant = "hero" }) {
  const navigate = useNavigate();
  const [sports, setSports] = useState([]);
  const [sport, setSport] = useState(initial.sport || "all");
  const [age, setAge] = useState(initial.age || "");
  const [cp, setCp] = useState(initial.postal_code || "");

  useEffect(() => {
    api.get("/sports").then(({ data }) => setSports(data)).catch(() => {});
  }, []);

  const submit = (e) => {
    e?.preventDefault();
    const params = new URLSearchParams();
    if (sport && sport !== "all") params.set("sport", sport);
    if (age) params.set("age", age);
    if (cp) params.set("postal_code", cp);
    navigate(`/clubs?${params.toString()}`);
  };

  const dark = variant === "hero";

  return (
    <form
      onSubmit={submit}
      data-testid="search-form"
      className={`grid gap-3 rounded-xl border p-3 sm:grid-cols-[1.4fr_1fr_1fr_auto] ${
        dark ? "border-white/10 bg-white shadow-2xl shadow-black/20" : "border-border bg-card"
      }`}
    >
      <div className="space-y-1.5">
        <Label className="overline text-muted-foreground">Sport</Label>
        <Select value={sport} onValueChange={setSport}>
          <SelectTrigger data-testid="search-sport" className="h-11 rounded-lg">
            <SelectValue placeholder="Tous les sports" />
          </SelectTrigger>
          <SelectContent className="max-h-72">
            <SelectItem value="all">Tous les sports</SelectItem>
            {sports.map((s) => (
              <SelectItem key={s.name} value={s.name}>
                {s.name} ({s.count})
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label className="overline text-muted-foreground">Age</Label>
        <Input
          data-testid="search-age"
          type="number"
          min={1}
          max={99}
          placeholder="Ex : 12"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          className="h-11 rounded-lg"
        />
      </div>

      <div className="space-y-1.5">
        <Label className="overline text-muted-foreground">Code postal (31)</Label>
        <Input
          data-testid="search-cp"
          placeholder="31000"
          value={cp}
          maxLength={5}
          onChange={(e) => setCp(e.target.value.replace(/\D/g, ""))}
          className="h-11 rounded-lg"
        />
      </div>

      <div className="flex items-end">
        <Button
          data-testid="search-submit"
          type="submit"
          className="h-11 w-full rounded-lg bg-sport px-6 font-bold text-white hover:bg-sport/90 sm:w-auto"
        >
          <Search className="mr-2 h-4 w-4" /> Faire du sport
        </Button>
      </div>
    </form>
  );
}
