using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;

public static class SaveLoadManager
{
    public static void Save(string path, List<Amalgam> amalgams)
    {
        var dtos = amalgams.Select(a => ToDto(a)).ToList();
        var json = JsonSerializer.Serialize(dtos, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(path, json);
        Console.WriteLine($"Saved {dtos.Count} amalgam(s) to {path}");
    }

    public static List<Amalgam> Load(string path)
    {
        if (!File.Exists(path))
        {
            Console.WriteLine("No save file found.");
            return new List<Amalgam>();
        }

        var json = File.ReadAllText(path);
        var dtos = JsonSerializer.Deserialize<List<AmalgamDto>>(json) ?? new List<AmalgamDto>();
        var list = dtos.Select(d => FromDto(d)).ToList();
        Console.WriteLine($"Loaded {list.Count} amalgam(s) from {path}");
        return list;
    }

    private static AmalgamDto ToDto(Amalgam a)
    {
        return new AmalgamDto
        {
            Name = a.GetName(),
            CurrentHealth = a.CurrentHealth,
            Parts = a.GetAllBodyParts().Select(p => new BodyPartDto
            {
                Type = p.GetType().Name,
                Name = p.GetName(),
                HealthStat = p.GetHealthStat(),
                AttackStat = p.GetAttackStat(),
                SpecialAbility = p.GetSpecialAbility(),
                TorsoHealAmount = (p is Torso t) ? t.GetHealAmount() : 0
            }).ToList()
        };
    }

    private static Amalgam FromDto(AmalgamDto dto)
    {
        var a = new Amalgam(dto.Name);
        foreach (var pd in dto.Parts)
        {
            BodyPart part = pd.Type switch
            {
                "Arms"  => new Arms(pd.HealthStat, pd.AttackStat, pd.SpecialAbility, pd.Name),
                "Ears"  => new Ears(pd.HealthStat, pd.AttackStat, pd.SpecialAbility, pd.Name),
                "Head"  => new Head(pd.HealthStat, pd.AttackStat, pd.SpecialAbility, pd.Name),
                "Hands" => new Hands(pd.HealthStat, pd.AttackStat, pd.SpecialAbility, pd.Name),
                "Legs"  => new Legs(pd.HealthStat, pd.AttackStat, pd.SpecialAbility, pd.Name),
                "Mouth" => new Mouth(pd.HealthStat, pd.AttackStat, pd.SpecialAbility, pd.Name),
                "Tail"  => new Tail(pd.HealthStat, pd.AttackStat, pd.SpecialAbility, pd.Name),
                "Torso" => new Torso(pd.HealthStat, pd.AttackStat, pd.SpecialAbility, pd.Name, pd.TorsoHealAmount),
                _ => throw new InvalidOperationException($"Unknown part type: {pd.Type}")
            };
            a.AddBodyPart(part);
        }

        a.CurrentHealth = dto.CurrentHealth;
        return a;
    }
}