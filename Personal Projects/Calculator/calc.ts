import * as readline from 'readline';

// `process` is provided by Node; with `@types/node` installed
// TypeScript will recognize it and provide proper types.

class Calculator {
  private pos = 0;
  private str = '';
  
  // ARRAY: A list of strings to store past equations
  public history: string[] = []; 

  // TUPLE: A fixed-length array holding [equationString, resultNumber]
  public lastCalculation: [string, number] | null = null; 

  public evaluate(input: string): number {
    this.str = input.replace(/\s+/g, '');
    this.pos = 0;
    
    if (this.str.length === 0) return 0;

    const result = this.parseExpression();

    if (this.pos < this.str.length) {
      throw new Error(`Unexpected character at index ${this.pos}: '${this.str[this.pos]}'`);
    }

    // Update the Array and Tuple before returning the result
    this.history.push(`${input} = ${result}`);
    this.lastCalculation = [input, result];

    return result;
  }
  
  // parsing functions (defined below)

  // Look at the current character without advancing
  private peek(): string {
    return this.pos < this.str.length ? this.str.charAt(this.pos) : '';
  }

  // Look at the current character and advance the position by 1
  private consume(): string {
    if (this.pos < this.str.length) {
      return this.str.charAt(this.pos++);
    }
    return '';
  }

  // 1. Handles Addition and Subtraction
  private parseExpression(): number {
    let left = this.parseTerm();

    while (this.peek() === '+' || this.peek() === '-') {
      const operator = this.consume();
      const right = this.parseTerm();
      
      if (operator === '+') {
        left += right;
      } else {
        left -= right;
      }
    }
    return left;
  }

  // 2. Handles Multiplication, Division, and implicit multiplication
  private parseTerm(): number {
    let left = this.parsePower();

    while (this.peek() === '*' || this.peek() === '/' || this.peek() === '(') {
      let operator = this.peek();

      if (operator === '(') {
        // Implicit multiplication, e.g. 3(4-2)
        operator = '*';
      } else {
        this.consume();
      }

      const right = this.parsePower();
      
      if (operator === '*') {
        left *= right;
      } else {
        left /= right;
      }
    }
    return left;
  }

  // 3. Handles Exponents (Powers)
  private parsePower(): number {
    let left = this.parsePrimary();

    // We use an 'if' here and recursively call parsePower to ensure 
    // right-associativity (e.g., 2^3^2 becomes 2^(3^2))
    if (this.peek() === '^') {
      this.consume();
      const right = this.parsePower();
      left = Math.pow(left, right);
    }
    return left;
  }

  // 4. Handles Numbers, Parentheses, and Negative/Positive signs
  private parsePrimary(): number {
    const char = this.peek();

    // Handle Unary minus (e.g., "-5")
    if (char === '-') {
      this.consume();
      return -this.parsePrimary();
    }
    
    // Handle Unary plus (e.g., "+5")
    if (char === '+') {
      this.consume();
      return this.parsePrimary();
    }

    // Handle Parentheses
    if (char === '(') {
      this.consume(); // Eat the '('
      const val = this.parseExpression(); // Recursively evaluate everything inside
      
      if (this.peek() === ')') {
        this.consume(); // Eat the ')'
      } else {
        throw new Error("Missing closing parenthesis ')'");
      }
      return val;
    }

    // Handle Numbers
    let numStr = '';
    // Keep consuming characters as long as they are digits or a decimal point
    while (this.pos < this.str.length && /[0-9.]/.test(this.peek())) {
      numStr += this.consume();
    }

    if (numStr === '') {
      throw new Error(`Expected a number or '(' at index ${this.pos}`);
    }

    return parseFloat(numStr);
  }
}

// --- Terminal CLI Setup ---

const calc = new Calculator();
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: 'calc> '
});

console.log("Terminal Calculator started. Type 'exit' to quit.");
rl.prompt();

rl.on('line', (line: string) => {
  const input = line.trim();
  
  if (input.toLowerCase() === 'exit' || input.toLowerCase() === 'quit') {
    process.exit(0);
  }

  if (input !== '') {
    try {
      const result = calc.evaluate(input);
      console.log(`= ${result}`);
    } catch (error: any) {
      console.error(`Error: ${error.message}`);
    }
  }
  
  rl.prompt();
}).on('close', () => {
  console.log('\nExiting calculator. Goodbye!');
  process.exit(0);
});