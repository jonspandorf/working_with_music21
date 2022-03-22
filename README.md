**Visualizing Music**

This is a project that visualizes musical notes of acoustic music. It can take orchestral scores and plot the notes on graph and help us get an overview of music scores.  

Music21 allows us to parse scores and get streams such as parts, measures, notes, rests, slurs and much more and we can expand on each stream and get it substreams. 

However, I could not find any stream that represents time such as beat, and since music is a form of art that occurs in time I had to find a workaround. 

This project takes each stream part, get's it's subelements and rebuild this on time. Once pitch frequencies are reproduced on timeline which consists of measures and beats, than it can be plotted on certain graphs which can teach us about compoers artistic decisions of there pieces. 
