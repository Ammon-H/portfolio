using System.Collections.Generic;

public class BodyPartDto
{
    public string Type { get; set; } = "";
    public string Name { get; set; } = "";
    public int HealthStat { get; set; }
    public int AttackStat { get; set; }
    public string SpecialAbility { get; set; } = "";
    public int TorsoHealAmount { get; set; } // only used when Type == "Torso"
}

public class AmalgamDto
{
    public string Name { get; set; } = "";
    public int CurrentHealth { get; set; }
    public List<BodyPartDto> Parts { get; set; } = new List<BodyPartDto>();
}