using System;
using System.Collections.Generic;

public class Amalgam
{
    public int CurrentHealth { get; set; }

    private List<BodyPart> _allBodyParts = new List<BodyPart>();
    private string _name;

    public Amalgam(string name)
    {
        _name = name;
        CurrentHealth = TotalHealth();  // will be zero at creation time

    }
    public Amalgam() {}

    public void PrepareForBattle()
{
    CurrentHealth = TotalHealth();
}

    public string GetName()
    {
        return _name;
    }

    public void AddBodyPart(BodyPart part)
    {
        _allBodyParts.Add(part);
    }

    public List<BodyPart> GetAllBodyParts()
    {
        return _allBodyParts;
    }

    public int TotalHealth()
    {
        int sum = 0;
        foreach (var part in _allBodyParts)
            sum += part.GetHealthStat();
        return sum;
    }

    public int TotalAttack()
    {
        int sum = 0;
        foreach (var part in _allBodyParts)
            sum += part.GetAttackStat();
        return sum;
    }
    public BodyPart GetRandomPart()
{
    var rand = new Random();
    int index = rand.Next(_allBodyParts.Count);
    return _allBodyParts[index];
}


    public void DisplayAmalgam()
    {
        Console.WriteLine($"=== {GetName()} ===");

        foreach (var part in _allBodyParts)
        {
            part.DisplayInfo();
            Console.WriteLine($"Special Ability: {part.GetSpecialAbility()}");
            Console.WriteLine();
        }

        Console.WriteLine($"Total Health: {TotalHealth()}");
        Console.WriteLine($"Total Attack: {TotalAttack()}");
        Console.WriteLine();
    }
}
