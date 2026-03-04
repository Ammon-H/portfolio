using System;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.IO;
class Program
{
    
public static void Fight(Amalgam a, Amalgam b)
{
    Console.WriteLine($"A battle begins between {a.GetName()} and {b.GetName()}!");
    Console.WriteLine();

    a.PrepareForBattle();
    b.PrepareForBattle();

    Random rand = new Random();

    while (a.CurrentHealth > 0 && b.CurrentHealth > 0)
    {
        // Attacker A
        BodyPart aPart = a.GetRandomPart();
        Console.WriteLine($"{a.GetName()} attacks!");
        aPart.Action();
        b.CurrentHealth -= aPart.GetAttackStat();
        Console.WriteLine($"{b.GetName()} takes {aPart.GetAttackStat()} damage! Current HP: {b.CurrentHealth}\n");

        if (b.CurrentHealth <= 0) break;

        // Attacker B
        BodyPart bPart = b.GetRandomPart();
        Console.WriteLine($"{b.GetName()} counter-attacks!");
        bPart.Action();
        a.CurrentHealth -= bPart.GetAttackStat();
        Console.WriteLine($"{a.GetName()} takes {bPart.GetAttackStat()} damage! Current HP: {a.CurrentHealth}\n");

        Console.WriteLine("Press ENTER for next turn...");
        Console.ReadLine();
    }

    Console.WriteLine("Battle Over!");
    Console.WriteLine(a.CurrentHealth > 0 ? $"{a.GetName()} wins!" : $"{b.GetName()} wins!");
}


    static void Main(string[] args)
    {
        List<Amalgam> amalgamons = new List<Amalgam>();
        bool running = true;

        while (running)
        {
            Console.WriteLine("Hello! Welcome to the world of Amalgamon!");
            Console.WriteLine("1. Create Amalgamon");
            Console.WriteLine("2. View Amalgamon");
            Console.WriteLine("3. Save Amalgamon");
            Console.WriteLine("4. Load Amalgamon");
            Console.WriteLine("5. Fight");
            Console.WriteLine("6. Quit");
            Console.Write("Choose an option: ");

            string choice = Console.ReadLine();
            Console.Clear();

            
            
            switch (choice)
            {
                case "1":
    
                    Console.Write("Name your Amalgam: ");
                    string name = Console.ReadLine();
                    Amalgam player = new Amalgam(name);
                    amalgamons.Add(player);


                    int partsamount = 0;
                    while (partsamount < 8)
                    {

                    Console.WriteLine("Select a body part to add:");
                    Console.WriteLine("1. Hands");
                    Console.WriteLine("2. Tail");
                    Console.WriteLine("3. Legs");
                    Console.WriteLine("4. Torso");
                    Console.WriteLine("5. Arms");
                    Console.WriteLine("6. Head");
                    Console.WriteLine("7. Mouth");
                    Console.WriteLine("8. Ears");

                    Console.Write("Choice: ");
                    int partChoice = int.Parse(Console.ReadLine());
                    switch(partChoice)
                    {
                        case 1:
                            Console.WriteLine("Adding Hands to your Amalgam.");
                            Console.Write("What would you like to name your Hands? ");
                            string handname =Console.ReadLine();
                            Console.Write("What ability do your Hands have? ");
                            string handability = Console.ReadLine();
                            Console.Write("What is the attack stat of your Hands? ");
                            int handattack = int.Parse(Console.ReadLine());
                            Console.Write("What is the health stat of your Hands? ");
                            int handhealth = int.Parse(Console.ReadLine());

                            player.AddBodyPart(new Hands(handhealth, handattack, handability, handname));
                            
                            break;

                        case 2:
                            Console.WriteLine("Adding Tail to your Amalgam.");
                            Console.Write("What would you like to name your Tail? ");
                            string tailName =Console.ReadLine();
                            Console.Write("What ability does your Tail have? ");
                            string tailAbility = Console.ReadLine();
                            Console.Write("What is the attack stat of your Tail? ");
                            int tailAttack = int.Parse(Console.ReadLine());
                            Console.Write("What is the health stat of your Tail? ");
                            int tailHealth = int.Parse(Console.ReadLine());
                            player.AddBodyPart(new Tail(tailHealth, tailAttack, tailAbility, tailName));
                            break;
                        case 3:
                            Console.WriteLine("Adding Legs to your Amalgam.");
                            Console.Write("What would you like to name your Legs? ");
                            string legName =Console.ReadLine();
                            Console.Write("What ability do your Legs have? ");
                            string legAbility = Console.ReadLine();
                            Console.Write("What is the attack stat of your Legs? ");
                            int legAttack = int.Parse(Console.ReadLine());
                            Console.Write("What is the health stat of your Legs? ");
                            int legHealth = int.Parse(Console.ReadLine());
                            player.AddBodyPart(new Legs(legHealth, legAttack, legAbility, legName));
                            break;
                        case 4:
                            Console.WriteLine("Adding Torso to your Amalgam.");
                            Console.Write("What would you like to name your Torso? ");
                            string torsoName =Console.ReadLine();
                            Console.Write("What ability does your Torso have? ");
                            string torsoAbility = Console.ReadLine();
                            Console.Write("What is the attack stat of your Torso? ");
                            int torsoAttack = int.Parse(Console.ReadLine());
                            Console.Write("What is the health stat of your Torso? ");
                            int torsoHealth = int.Parse(Console.ReadLine());
                            Console.Write("How much can your Torso heal? ");
                            int healAmount = int.Parse(Console.ReadLine());
                            player.AddBodyPart(new Torso(torsoHealth, torsoAttack, torsoAbility, torsoName, healAmount));
                            break;
                        case 5:
                            Console.WriteLine("Adding Arms to your Amalgam.");
                            Console.Write("What would you like to name your Arms? ");
                            string armName =Console.ReadLine();
                            Console.Write("What ability do your Arms have? ");
                            string armAbility = Console.ReadLine();
                            Console.Write("What is the attack stat of your Arms? ");
                            int armAttack = int.Parse(Console.ReadLine());
                            Console.Write("What is the health stat of your Arms? ");
                            int armHealth = int.Parse(Console.ReadLine());
                            player.AddBodyPart(new Arms(armHealth, armAttack, armAbility, armName));
                            break;
                        case 6:
                            Console.WriteLine("Adding Head to your Amalgam.");
                            Console.Write("What would you like to name your Head? ");
                            string headName =Console.ReadLine();
                            Console.Write("What ability does your Head have? ");
                            string headAbility = Console.ReadLine();
                            Console.Write("What is the attack stat of your Head? ");
                            int headAttack = int.Parse(Console.ReadLine());
                            Console.Write("What is the health stat of your Head? ");
                            int headHealth = int.Parse(Console.ReadLine());
                            player.AddBodyPart(new Head(headHealth, headAttack, headAbility, headName));
                            break;
                        case 7:
                            Console.WriteLine("Adding Mouth to your Amalgam.");
                            Console.Write("What would you like to name your Mouth? ");
                            string mouthName =Console.ReadLine();
                            Console.Write("What ability does your Mouth have? ");
                            string mouthAbility = Console.ReadLine();
                            Console.Write("What is the attack stat of your Mouth? ");
                            int mouthAttack = int.Parse(Console.ReadLine());
                            Console.Write("What is the health stat of your Mouth? ");
                            int mouthHealth = int.Parse(Console.ReadLine());
                            player.AddBodyPart(new Mouth(mouthHealth, mouthAttack, mouthAbility, mouthName));
                            break;
                        case 8:
                            Console.WriteLine("Adding Ears to your Amalgam.");
                            Console.Write("What would you like to name your Ears? ");
                            string earName =Console.ReadLine();
                            Console.Write("What ability do your Ears have? ");
                            string earAbility = Console.ReadLine();
                            Console.Write("What is the attack stat of your Ears? ");
                            int earAttack = int.Parse(Console.ReadLine());
                            Console.Write("What is the health stat of your Ears? ");
                            int earHealth = int.Parse(Console.ReadLine());
                            player.AddBodyPart(new Ears(earHealth, earAttack, earAbility, earName));
                            break;

                        default:
                            Console.WriteLine("Invalid choice.");
                            continue;
                    }
                    partsamount++;
                    Console.WriteLine($"Body parts added: {partsamount}/8\n");
                }
                    break;
            
                
                    
                    

                case "2":
                    foreach (var a in amalgamons)
                    {
                        a.DisplayAmalgam();
                    }
                    break;
                case "3":
                    SaveLoadManager.Save("amalgams.json", amalgamons);
                    break;
                case "4":
                    amalgamons = SaveLoadManager.Load("amalgams.json");
                    break;
                case "5":
    if (amalgamons.Count < 2)
    {
        Console.WriteLine("You need at least 2 Amalgams to fight!");
        break;
    }

                Console.WriteLine("Choose your fighter:");
                for (int i = 0; i < amalgamons.Count; i++)
            Console.WriteLine($"{i+1}. {amalgamons[i].GetName()}");

                Console.Write("Choice: ");
                int fighter1 = int.Parse(Console.ReadLine()) - 1;

                Console.WriteLine("Choose opponent:");
                for (int i = 0; i < amalgamons.Count; i++)
                Console.WriteLine($"{i+1}. {amalgamons[i].GetName()}");

                Console.Write("Choice: ");
                int fighter2 = int.Parse(Console.ReadLine()) - 1;

            Fight(amalgamons[fighter1], amalgamons[fighter2]);
            break;

                case "6":
                    running = false;
                    break;

                default:
                    Console.WriteLine("Invalid choice.");
                    break;
            }
        }
    }

    
}
