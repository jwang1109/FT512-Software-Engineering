describe("statement", function() {
  it("generates 'Refactoring' 2nd ed example output", function() {
    expected1 = "<h1>Statement for BigCo</h1>\n<table>\n<tr><th>play</th><th>seats</th><th>cost</th></tr>  <tr><td>Hamlet</td><td>55</td><td>$650.00</td></tr>\n  <tr><td>As You Like It</td><td>35</td><td>$580.00</td></tr>\n  <tr><td>Othello</td><td>40</td><td>$500.00</td></tr>\n</table>\n<p>Amount owed is <em>$1,730.00</em></p>\n<p>You earned <em>47</em> credits</p>\n"

      assert.equal(statement(invoice1[0],plays1), expected1);
  });

    // Example adapted from https://github.com/emilybache/Theatrical-Players-Refactoring-Kata/blob/main/javascript/test/statement.test.js
    it("test missing play type (Bache Kata example output)", function() {
      //chai.expect(function() {statement(invoice2,plays2)}).to.throw("unknown type: history");
      assert.throws(() => statement(invoice2,plays2), "unknown type: history");
    });
});
