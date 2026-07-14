using System;

public class Head : BodyPart
{
    public Head(int healthStat, int attackStat, string specialAbility, string name)
        : base(name, healthStat, attackStat, specialAbility)
    {
    }


    public override void Action()
    {
        Console.WriteLine($"Your amalgam charges forward with its {GetName()} using {GetSpecialAbility}!");
    }
}