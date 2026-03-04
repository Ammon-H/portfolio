using System;

public class Mouth : BodyPart
{
    public Mouth(int healthStat, int attackStat, string specialAbility, string name)
        : base(name, healthStat, attackStat, specialAbility)
    {
    }

    public override void Action()
    {
        Console.WriteLine($"Your amalgam {GetSpecialAbility()} fiercely with its {GetName()}!");
    }
}