using System;

public class Ears : BodyPart
{
    public Ears(int healthStat, int attackStat, string specialAbility, string name)
        : base(name, healthStat, attackStat, specialAbility)
    {}
    public override void Action()
    {
        Console.WriteLine($"Your amalgam listens carefully with its {GetName()} using {GetSpecialAbility()}!");

    }
}