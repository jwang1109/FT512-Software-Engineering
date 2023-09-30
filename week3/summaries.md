# Your paper and video summaries go here.

# Rubric:
* Write a short summary of the paper/video, as follows:
* First line: Paper Title, citation source
* Keywords: List keywords from paper, or select 4-8 most relevant terms from the paper
* First paragraph: describe the main points of the paper/video.
* Second paragraph: Present the paper/video's strengths and weaknesses from your point of view.


# Parnas, D. "On the Criteria to be used in Decomposing Systems into Modules." Communications of the ACM, vol. 15, no. 12, 1972, pp. 1053-1058, doi:10.1145/361598.361623.

Keyword: decomposition, efficiency, program design, KWIC indexing, modules

Summary:
This article mainly discussed two decompositions of a KWIC indexing system. The author concludes that people should apply an unconventional decomposition, which may be more efficient. The decomposition focuses on a module that hides design decisions from others and allows different modules' codes to be assembled.

After reviewing my code, I found my code looks more like the first decomposition than the second one. Each major step is made into its module. The data passed through those steps and finally reached the result. There is no hidden information behind any steps. I also assembled the modules, not codes from different modules. However, I do apply some principles mentioned in class. Eg. One responsibility for one component.

Strength:
* The article is foresighted. The idea of hiding design decisions sounds like encapsulation in OOP. The idea of assembling collections of code from various modules sounds like methods in OOP. This article may be an early-stage prototype of OOP
* A detailed example is provided.

Weakness:
* The article is too old and offers little clue about the design in the current era. 
* Before generalizing the conclusion, the author should provide more evidence. KWIC example might only be coincident.


# Modern Code Review. Source: Oram, A., Wilson, G. (2011) Making software: What really works, and why we believe it. O'Reilly.

Keywords: code review, defects, efficiency,
LOC, false-positives, reviewer, meeting

The article proposes several best practices for code review. We should only spend 60-90 minutes on code review due to focus fatigue. 400 LOC/hour is the most efficient speed. Additionally, context can help find defects. The article also discusses whether we need a meeting to review codes. The statistics show that only 4% of defects are found in a meeting. However, those defects are more subtle, and the meeting can detect many false positives. Finally, the article also found that self-review can also be effective, so whether an independent reviewer is necessary depends on the situation.

Strength: 
* Statistics and charts support ideas, thus making them convincing and easy to understand
* Offers practical view and suggestions on code review.

Weakness:
* Some suggestions are not decisive and thus can't support the final decision. (eg. Do we need an independent reviewer?)



# GORUCO2009 - SOLID Object-Oriented Design by Sandi Metz. Source: https://www.youtube.com/watch?v=v-2yFMzxqwU
Summaries:
The lecturer talks about how good design can save programmers—a good design saves time and money in the long run. To achieve independence, we will find SOLID principles helpful, S for single responsibility, O for being open to extension but closed for modification, L for Liskov substitution, I for interface segregation, and D for Dependency Inversion. Resistance is resources. Perform TDD, and every time test cases fail, we fix that. At the same, we should also ask four questions: Is it DRY? Does it only have one single responsibility? Does everything changes at the same rate? Does it depend on things that change more often than itself?

Keywords: SOLID principles, dependency injection, TDD, design philosophy, Ruby

Strength:
* It helped me review concepts like SOLID principles, TDD
* The lecturer proposed four questions that can help us when we are refactoring.

Weakness: 
* The lecturer takes codes written in Ruby as an example, which is unfamiliar and prevents me from understanding examples.

# Rediscovering Simplicity Source: Sandi Metz, Katrina Owen, TJ Stankus, (2020) Bottles of OOP, 2nd edition

The author introduced four implementations of 99 bottles. Those implementations have violated many design principles and become very ugly. We can measure code quality by some good metrics, such as SLOC and the number of lines of source code and  ABC(assignments, branches, and Conditions). By comparing the SLOC and ABC metrics of
the four solutions mentioned before, the author clearly showed which implementation is the clearest and easiest.

Keywords: LOC, AMC, code review, code quality

Strength:
* Beautiful charts and tables help introduce SLOC and AMC. The article clearly explains those two concepts.
Weakness:
* Ninety-nine bottles are not a good example. Those four implementations are so weird that I don't believe a programmer would write that kind of code for such a simple problem, which can be solved by only several lines of code and two or three conditions. 
* The author only discusses toy problems and can't generalize the use of those metrics.
* The author also ignored the cost of conducting code reviews. It would be no easy work to do SLOC, and AMC counts. Is there any pre-built program to help count those metrics?