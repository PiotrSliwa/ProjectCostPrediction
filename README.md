# ProjectCostPrediction
Predictive model forecasting open source project cost based on registered issues.

The project was a part of Master's Thesis which proposed a method of identification for intellectual capital accumulated in an organization. A hypothesis was that one can observe the intellectual capital by correlating differences in the organization's material state and its effective value.

To test this hypothesis, several open-source projects were examined. The research method assumed their cost can be indirectly represented using CoCoMo model which ties the cost with modified lines of code.

The project consists of two sub-projects:

* `importer` - scripts extracting and transforming publicly available data from various open-source projects
* `forecaster` - predictive model built with scikit-learn, analyzing projects' discussions and forecasting their cost