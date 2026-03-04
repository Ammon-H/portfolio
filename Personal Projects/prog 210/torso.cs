using System;

public class Torso : BodyPart
{
    private int _healAmount;
    public Torso(int healthStat, int attackStat, string specialAbility, string name, int healAmount)
        : base(name, healthStat, attackStat, specialAbility)
    {
        _healAmount = healAmount;
    }
    public override void Action()
    {
        Console.WriteLine($"Your amalgam uses its {GetName()} to heal for {_healAmount} using {GetSpecialAbility()}!");
    }
public int GetHealAmount()
{
    return _healAmount;
}
}
