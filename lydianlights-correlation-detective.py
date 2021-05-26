# algorithm: correlation-detective
# by: lydianlights

# try to guess how our actions correlate to our opponent's actions
TRIAL_PERIOD = 10
HISTORY_TEST_DEPTH = 3
MIN_SAMPLE_SIZE = 3
CERTAINTY_THRESHOLD = 0.8
CORRELATION_THRESHOLD = 0.65
PRIORITY_THRESHOLD = 0.3


def strategy(history, memory):
  numTurns = history.shape[1]
  # start with titForTat
  if numTurns < TRIAL_PERIOD:
    return titForTat(history), None

  # check if our past actions seem to have influenced the opponent
  n = min(numTurns, HISTORY_TEST_DEPTH)
  correlationsList = [calcCorrelations(
      history[0], history[1][i:]) for i in range(1, n + 1)]
  defectPrediction, coopPrediction = evalCorrelations(correlationsList)

  # we think opponent will coop when we defect -- take full advantage
  if defectPrediction > CERTAINTY_THRESHOLD:
    return 0, None

  # we think opponent will coop when we coop -- work together
  if coopPrediction > CERTAINTY_THRESHOLD:
    return 1, None

  # we think opponent will defect on us -- defect in return
  if defectPrediction < -CERTAINTY_THRESHOLD or coopPrediction < -CERTAINTY_THRESHOLD:
    return 0, None

  # we think the opponent is watching us but we're unsure of their strategy
  if abs(defectPrediction) > CORRELATION_THRESHOLD or abs(coopPrediction) > CORRELATION_THRESHOLD:
    return titForTat(history), None

  # we think opponent is unpredictable, so treat them like a random agent
  return 0, None


# === Strategies === #
def titForTat(history):
  if history.shape[1] > 0 and history[1, -1] == 0:
    return 0
  return 1


# === Calculations === #
def calcCorrelations(myList, oppList):
  defCausesDef_count = 0
  defCausesCoop_count = 0
  coopCausesDef_count = 0
  coopCausesCoop_count = 0
  defectCount = 0
  coopCount = 0
  for a, b in zip(myList, oppList):
    if a == 0:
      defectCount += 1
      if b == 0:
        defCausesDef_count += 1
      elif b == 1:
        defCausesCoop_count += 1
    elif a == 1:
      coopCount += 1
      if b == 0:
        coopCausesDef_count += 1
      elif b == 1:
        coopCausesCoop_count += 1

  result = (
      createCorrelation(defCausesDef_count, defectCount),
      createCorrelation(defCausesCoop_count, defectCount),
      createCorrelation(coopCausesDef_count, coopCount),
      createCorrelation(coopCausesCoop_count, coopCount)
  )
  return result


def createCorrelation(hits, sampleSize):
  strength = 0
  if sampleSize > MIN_SAMPLE_SIZE:
    strength = hits / sampleSize
  return {
      "strength": strength,
      "sampleSize": sampleSize
  }


def evalCorrelations(correlationsList):
  bestCorrelations = [None] * 4
  for listIndex, correlations in enumerate(correlationsList, start=1):
    for elementIndex, correlation in enumerate(correlations):
      if bestCorrelations[elementIndex] == None or bestCorrelations[elementIndex]["strength"] < correlation["strength"]:
        bestCorrelations[elementIndex] = {
            "strength": correlation["strength"],
            "sampleSize": correlation["sampleSize"],
            "offset": listIndex
        }

  # give priority to correlations that show apparent cooperation
  if bestCorrelations[1]["strength"] > PRIORITY_THRESHOLD:
    defectPrediction = bestCorrelations[1]["strength"]
  else:
    defectPrediction = bestCorrelations[1]["strength"] - bestCorrelations[0]["strength"]

  if bestCorrelations[3]["strength"] > PRIORITY_THRESHOLD:
    coopPrediction = bestCorrelations[3]["strength"]
  else:
    coopPrediction = bestCorrelations[3]["strength"] - bestCorrelations[2]["strength"]

  return defectPrediction, coopPrediction
