# Your paper and video summaries go here.

# Rubric:
* Write a short summary of the paper/video, as follows:
* First line: Paper Title, citation source
* Keywords: List keywords from paper, or select 4-8 most relevant terms from the paper
* First paragraph: describe the main points of the paper/video.
* Second paragraph: Present the paper/video's strengths and weaknesses from your point of view.



# Kevlin Henney, The SOLID Design Principles Deconstructed Source: www.youtube.com/watch?v=tMW08JkFrBA

The presenter explains SOLID principles and some other essential concepts to the audience. 
* SRP(Single Responsibility Principle): A class should have one and only one reason to change, meaning that a class should have only one job.
* OCP(open-closed principle): Objects or entities should be open for extension but closed for modification.
* LSP(Liskov substitution Principle): Let q(x) be a property provable about objects of x of type T. Then q(y) should be provable for objects y of type S where S is a subtype of T.
* ISP(Interface segregation Principle): A client should never be forced to implement an interface that it doesn’t use, or clients shouldn’t be forced to depend on methods they do not use.
* DIP(Dependency Inversion Principle): Entities must depend on abstractions, not concretions. It states that the high-level module must not depend on the low-level module, but they should depend on abstractions.

The presenter also explained coupling and cohesion. Coupling is interdependency between different modules. It should be low. Cohesion is something hanging together and working together. Its behavior must not contradict any superclass expectations but could have additional behaviors. So, gather together those things changing for the same reason and separate those that change for different reasons. 

Strength:

1. He explained the principles by widely-used example, which helped him to deliver the message well.

Weakness:
1. The presenter obviously hurries to end the presentation because of bad time control. So he explained some of the principles in detail while others are not.

2. No concrete implementations guidance are provided. SOLID principles are abstract.