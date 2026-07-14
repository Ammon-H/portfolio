using System;
public class Tail : BodyPart
{
    public Tail(int healthStat, int attackStat, string specialAbility, string name)
        : base(name, healthStat, attackStat, specialAbility)
    {
    }

    public override void Action()
    {
        Console.WriteLine($"Your amalgam {GetSpecialAbility()}s with its {GetName()}!");
    }
}