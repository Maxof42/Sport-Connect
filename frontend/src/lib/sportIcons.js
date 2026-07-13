import {
  Dumbbell, Trophy, Waves, Bike, Mountain, Music, Target, Sailboat,
  Snowflake, Volleyball, Zap, Activity, Footprints, Circle, Swords,
} from "lucide-react";

const ICONS = {
  "Tennis": Circle,
  "Tennis de table": Circle,
  "Football": Volleyball,
  "Rugby": Trophy,
  "Basketball": Volleyball,
  "Handball": Volleyball,
  "Volley-ball": Volleyball,
  "Badminton": Zap,
  "Squash": Circle,
  "Natation": Waves,
  "Athletisme": Footprints,
  "Petanque": Target,
  "Equitation": Activity,
  "Golf": Target,
  "Skate / Roller": Bike,
  "Escalade": Mountain,
  "Danse": Music,
  "Arts martiaux": Swords,
  "Fitness / Musculation": Dumbbell,
  "Cyclisme": Bike,
  "Tir": Target,
  "Sports nautiques": Sailboat,
  "Patinage": Snowflake,
  "Pelote basque": Circle,
  "Baseball": Trophy,
  "Hockey": Trophy,
  "Gymnastique": Activity,
  "Multisports": Dumbbell,
};

export function sportIcon(sport) {
  return ICONS[sport] || Dumbbell;
}
