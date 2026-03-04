using System;

public class Arms: BodyPart
{
    public Arms(int healthStat, int attackStat, string specialAbility, string name)
        : base(name, healthStat, attackStat, specialAbility)
    {
    }


    public override void Action()
    {
        Console.WriteLine($"Your amalgum blocks with its {GetName()} using {GetSpecialAbility()}!");
    }
}