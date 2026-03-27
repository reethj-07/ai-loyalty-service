from datetime import datetime, timedelta, timezone

from app.ml.rfm_engine import RFMEngine



def test_dormant_member_gets_low_rfm_score():
    """Member with last purchase 180 days ago scores R=1"""
    engine = RFMEngine()
    now = datetime.now(timezone.utc)
    transactions = [
        {
            "member_id": "dormant-1",
            "amount": 50,
            "transaction_date": (now - timedelta(days=180)).isoformat(),
        }
    ]

    scored = engine.score_to_quintiles(engine.compute_rfm_dataframe(transactions))
    row = scored.iloc[0]

    assert int(row["R_score"]) == 1



def test_champion_member_scores_above_4():
    """Weekly buyer with $1000+ monthly spend scores >= 4.0"""
    engine = RFMEngine()
    now = datetime.now(timezone.utc)

    transactions = []
    for i in range(12):
        transactions.append(
            {
                "member_id": "champion-1",
                "amount": 280,
                "transaction_date": (now - timedelta(days=i * 7)).isoformat(),
            }
        )

    scored = engine.score_to_quintiles(engine.compute_rfm_dataframe(transactions))
    row = scored.iloc[0]

    assert float(row["rfm_score"]) >= 4.0
