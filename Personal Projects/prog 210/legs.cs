using System;
public class Legs : BodyPart
{

    public Legs(int healthStat, int attackStat, string specialAbility, string name)
        : base(name, healthStat, attackStat, specialAbility)
    {
    }
 public  override void Action()
    {
        Console.WriteLine($"Your amalgam {GetSpecialAbility()}s swiftly with its {GetName()}!");
    }

}