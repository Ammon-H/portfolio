using System;

public class Hands : BodyPart
{
    public Hands(int healthStat, int attackStat, string specialAbility, string name)
        : base(name, healthStat, attackStat, specialAbility)
    {
    }
    public override void Action()
    {
        Console.WriteLine($"Your amalgam {GetSpecialAbility}s using {GetName}!");
    }
}