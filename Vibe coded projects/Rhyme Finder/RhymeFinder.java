// ============================================================
//  IMPORTS
//  Java doesn't give you everything automatically.
//  You have to "import" tools from its standard library.
//  Think of it like adding ingredients before you cook.
// ============================================================

import java.nio.file.*;      // gives us: Files, Paths  (for reading files)
import java.io.*;            // gives us: IOException    (for handling file errors)
import java.util.*;          // gives us: HashMap, ArrayList, Arrays, Collections, Scanner

// ============================================================
//  THE CLASS
//  Every Java program lives inside a class.
//  The class name must exactly match the filename.
//  This file is RhymeFinder.java, so the class is RhymeFinder.
// ============================================================

public class RhymeFinder {

    // ============================================================
    //  THE DICTIONARY FIELD
    //
    //  This is a "field" — a variable that belongs to the whole
    //  class, not just one method. Any method can read or change it.
    //
    //  HashMap<String, String[]>  means:
    //    - Keys   are Strings       (the word,     e.g. "moon")
    //    - Values are String arrays (the phonemes, e.g. ["M","UW1","N"])
    //
    //  "static" means it belongs to the class itself, not to any
    //  specific object created from the class. Since we're not
    //  creating objects here, all our fields and methods are static.
    // ============================================================

    static HashMap<String, String[]> dictionary = new HashMap<>();

    // ============================================================
    //  METHOD: loadDictionary
    //
    //  This method reads the cmudict.dict file line by line
    //  and fills the HashMap above.
    //
    //  "throws IOException" means: this method might fail if the
    //  file doesn't exist. We're telling Java "I know, just let
    //  the error bubble up to main() and we'll handle it there."
    // ============================================================

    static void loadDictionary(String filePath) throws IOException {

        // Files.readAllLines reads every line of the file into a List.
        // Paths.get turns the filename string into a file path object.
        // The result is a List<String> — like an array, but resizable.
        List<String> lines = Files.readAllLines(Paths.get(filePath));

        // Loop through every line in the file.
        // "String line : lines" means "for each line in lines"
        for (String line : lines) {

            // CMUdict has comment lines that start with ";;;". Skip them.
            if (line.startsWith(";;;")) {
                continue;   // "continue" jumps to the next loop iteration
            }

            // Skip any empty lines (just in case)
            if (line.trim().isEmpty()) {
                continue;
            }

            // Split the line on whitespace.
            // "\\s+" is a regex pattern meaning "one or more spaces/tabs".
            // Result for "moon  M UW1 N" -> ["moon", "M", "UW1", "N"]
            String[] parts = line.split("\\s+");

            // If splitting gave us fewer than 2 parts, the line is malformed.
            // Skip it to avoid crashes.
            if (parts.length < 2) {
                continue;
            }

            // parts[0] is the word. Convert to lowercase for consistency.
            String word = parts[0].toLowerCase();

            // CMUdict marks alternate pronunciations like "word(2)", "word(3)".
            // We only want the first pronunciation, so skip lines where the
            // word contains a parenthesis.
            if (word.contains("(")) {
                continue;
            }

            // parts[1] through parts[parts.length - 1] are the phonemes.
            // Arrays.copyOfRange(array, start, end) copies a slice of an array.
            // start is inclusive, end is exclusive.
            // So this copies from index 1 to the last index -> the phonemes only.
            String[] phonemes = Arrays.copyOfRange(parts, 1, parts.length);

            // Store in the HashMap: word -> phonemes
            dictionary.put(word, phonemes);
        }

        // Print how many words were loaded so we know it worked.
        System.out.println("Dictionary loaded: " + dictionary.size() + " words.");
    }

    // ============================================================
    //  METHOD: getRhymeTail
    //
    //  Given a phoneme array, returns the "rhyming tail" --
    //  everything from the last stressed vowel to the end.
    //
    //  In ARPAbet, vowels have a number at the end:
    //    "1" = primary stress   (e.g. "UW1")
    //    "2" = secondary stress (e.g. "AH2")
    //    "0" = unstressed       (e.g. "AH0")
    //
    //  For rhyming we care about the last STRESSED vowel (1 or 2).
    //  Example: ["B","AH0","L","UW1","N"] -> tail is ["UW1","N"]
    //           ["M","UW1","N"]           -> tail is ["UW1","N"]
    //           Both rhyme!
    //
    //  Input:  String[] phonemes  -- the full phoneme array
    //  Output: String[]           -- the rhyming tail
    // ============================================================

    static String[] getRhymeTail(String[] phonemes) {

        // Loop BACKWARDS through the phoneme array.
        // We start at the last index (phonemes.length - 1) and go down to 0.
        for (int i = phonemes.length - 1; i >= 0; i--) {

            String phoneme = phonemes[i];

            // Check if this phoneme is a STRESSED vowel.
            // endsWith("1") catches primary stress, endsWith("2") catches secondary.
            if (phoneme.endsWith("1") || phoneme.endsWith("2")) {

                // Found the last stressed vowel!
                // Return everything from here to the end of the array.
                return Arrays.copyOfRange(phonemes, i, phonemes.length);
            }
        }

        // If no stressed vowel found (rare), return the whole array as fallback.
        return phonemes;
    }

    // ============================================================
    //  METHOD: countRhymingSyllables
    //
    //  Given a rhyme tail, count how many syllables are in it.
    //  Each vowel phoneme in the tail = 1 syllable.
    //
    //  We use this to RANK rhymes:
    //    "moon" vs "balloon"   -> tail ["UW1","N"]   -> 1 syllable
    //    "delight" vs "moonlight" -> tail ["AY1","T"] -> 1 syllable
    //    "entertain" vs "again"   -> different tails  -> 0 (no match)
    //
    //  Input:  String[] tail -- the rhyme tail of the matched word
    //  Output: int           -- number of rhyming syllables
    // ============================================================

    static int countRhymingSyllables(String[] tail) {
        int count = 0;

        // Loop through each phoneme in the tail
        for (String phoneme : tail) {

            // Vowel phonemes end in 0, 1, or 2.
            // If the last character is a digit, it's a vowel -> 1 syllable.
            char lastChar = phoneme.charAt(phoneme.length() - 1);

            // Character.isDigit() returns true if the character is 0-9.
            if (Character.isDigit(lastChar)) {
                count++;  // found a vowel = one more syllable
            }
        }

        return count;
    }

    // ============================================================
    //  METHOD: findRhymes
    //
    //  Looks up the input word, gets its rhyme tail, then scans
    //  the entire dictionary for words with the same tail.
    //  Returns results grouped by how many syllables rhyme.
    //
    //  Input:  String inputWord -- the word to rhyme
    //  Output: TreeMap<Integer, ArrayList<String>>
    //            keys   = number of rhyming syllables (sorted descending)
    //            values = list of words with that many rhyming syllables
    // ============================================================

    static TreeMap<Integer, ArrayList<String>> findRhymes(String inputWord) {

        // Convert to lowercase so lookup is case-insensitive
        inputWord = inputWord.toLowerCase().trim();

        // Look up the word in our HashMap.
        // .get() returns the value (phoneme array), or null if not found.
        String[] inputPhonemes = dictionary.get(inputWord);

        // If the word isn't in the dictionary, we can't rhyme it.
        // Return an empty TreeMap.
        if (inputPhonemes == null) {
            System.out.println("  \"" + inputWord + "\" was not found in the dictionary.");
            return new TreeMap<>();
        }

        // Get the rhyming tail for the input word.
        String[] inputTail = getRhymeTail(inputPhonemes);

        // TreeMap automatically sorts by key.
        // Collections.reverseOrder() makes it sort DESCENDING (3,2,1 not 1,2,3).
        // This way "best rhymes" (most syllables) appear first.
        TreeMap<Integer, ArrayList<String>> results = new TreeMap<>(Collections.reverseOrder());

        // Now scan EVERY word in the dictionary.
        // entrySet() gives us a set of key-value pairs we can loop over.
        for (Map.Entry<String, String[]> entry : dictionary.entrySet()) {

            String candidate  = entry.getKey();    // the word
            String[] phonemes = entry.getValue();  // its phonemes

            // Don't compare the word to itself
            if (candidate.equals(inputWord)) {
                continue;
            }

            // Get the rhyming tail of this candidate word
            String[] candidateTail = getRhymeTail(phonemes);

            // Arrays.equals() compares two arrays element by element.
            // (You can't use == for arrays in Java -- that checks identity, not content.)
            if (Arrays.equals(inputTail, candidateTail)) {

                // The tails match -- this word rhymes!
                // Count how many syllables are in the shared tail.
                int syllables = countRhymingSyllables(candidateTail);

                // computeIfAbsent: if the key doesn't exist yet in the TreeMap,
                // create a new ArrayList for it. Then add the word to that list.
                // This is shorthand for:
                //   if (!results.containsKey(syllables)) results.put(syllables, new ArrayList<>());
                //   results.get(syllables).add(candidate);
                results.computeIfAbsent(syllables, k -> new ArrayList<>()).add(candidate);
            }
        }

        // Sort each group alphabetically (TreeMap handles the syllable sorting,
        // but within each group the words are in insertion order by default).
        for (ArrayList<String> group : results.values()) {
            Collections.sort(group);
        }

        return results;
    }

    // ============================================================
    //  METHOD: displayResults
    //
    //  Prints the rhyme results neatly, grouped by syllable count.
    //
    //  Input: String inputWord                               -- the original word
    //         TreeMap<Integer, ArrayList<String>> results   -- from findRhymes()
    // ============================================================

    static void displayResults(String inputWord, TreeMap<Integer, ArrayList<String>> results) {

        System.out.println("\n+==================================================+");
        System.out.printf ("  Rhymes for: \"%s\"%n", inputWord);
        System.out.println("+==================================================+");

        // If no rhymes were found, say so and return early.
        if (results.isEmpty()) {
            System.out.println("  No rhymes found.");
            return;
        }

        // Count total rhymes across all groups
        int total = 0;
        for (ArrayList<String> group : results.values()) {
            total += group.size();
        }

        // Loop through each syllable group (3 syllables, then 2, then 1, etc.)
        // entrySet() gives us the key (syllable count) and value (word list) together.
        for (Map.Entry<Integer, ArrayList<String>> entry : results.entrySet()) {

            int syllableCount       = entry.getKey();
            ArrayList<String> words = entry.getValue();

            // Print the group header
            System.out.printf("%n  -- %d rhyming syllable(s) (%d words) --%n",
                              syllableCount, words.size());

            // Print words in rows of 5 for readability
            int col = 0;
            for (String word : words) {
                // %-18s means: left-align the string in a field 18 chars wide
                System.out.printf("  %-18s", word);
                col++;

                // After every 5 words, print a newline to start a new row
                if (col % 5 == 0) {
                    System.out.println();
                }
            }

            // If the last row wasn't complete, we still need a newline
            if (col % 5 != 0) {
                System.out.println();
            }
        }

        System.out.println("\n  Total rhymes found: " + total);
        System.out.println();
    }

    // ============================================================
    //  METHOD: main
    //
    //  This is where Java starts running your program.
    //  String[] args lets users pass arguments on the command line
    //  (we won't use it here, but it's required by Java).
    // ============================================================

    public static void main(String[] args) {

        System.out.println("+==================================================+");
        System.out.println("         R H Y M E   F I N D E R                    ");
        System.out.println("       Powered by the CMU Pronouncing Dict           ");
        System.out.println("+==================================================+");

        // Load the dictionary first.
        // We wrap it in try/catch because file reading can fail --
        // for example if cmudict.dict doesn't exist in this folder.
        //
        // try  { ... }  -- attempt this code
        // catch { ... } -- if an IOException occurs, run this instead
        try {
            loadDictionary("cmudict.dict");
        } catch (IOException e) {
            // e.getMessage() gives a human-readable description of what went wrong.
            System.out.println("Error loading dictionary: " + e.getMessage());
            System.out.println("Make sure cmudict.dict is in the same folder as this program.");
            return;  // Stop the program -- we can't continue without the dictionary
        }

        // Scanner reads user input from the keyboard.
        // System.in is the "standard input" stream (the keyboard).
        Scanner scanner = new Scanner(System.in);

        // Keep asking for words until the user types "quit"
        while (true) {
            System.out.print("\nEnter a word to rhyme (or 'quit' to exit): ");

            // scanner.nextLine() waits for the user to press Enter and returns
            // whatever they typed as a String.
            String input = scanner.nextLine().trim();

            // Check if the user wants to quit
            if (input.equalsIgnoreCase("quit") || input.equalsIgnoreCase("exit")) {
                System.out.println("\nGoodbye! Keep rhyming!\n");
                break;  // "break" exits the while loop entirely
            }

            // Don't process empty input
            if (input.isEmpty()) {
                System.out.println("  Please enter a word.");
                continue;  // jump back to the top of the while loop
            }

            // Find and display the rhymes
            TreeMap<Integer, ArrayList<String>> rhymes = findRhymes(input);
            displayResults(input, rhymes);
        }

        // Always close the Scanner when you're done -- good practice
        scanner.close();
    }
}