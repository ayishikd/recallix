import re

message1 = "Galaxy X-55 primary emission is Synchrotron Radiation."
message2 = "ALERT: Galaxy X-55 has shifted states. Primary emission is now Inverse Compton Scattering."

e_match1 = re.search(r"\b(Galaxy X-\d+|Project [A-Z][a-z]+)\b", message1, re.IGNORECASE)
e_match2 = re.search(r"\b(Galaxy X-\d+|Project [A-Z][a-z]+)\b", message2, re.IGNORECASE)

print(f"Match 1: {e_match1.group(1) if e_match1 else 'NONE'}")
print(f"Match 2: {e_match2.group(1) if e_match2 else 'NONE'}")

r_match1 = re.search(r"\b(primary emission|status|location|security|primary cause)\b", message1, re.IGNORECASE)
r_match2 = re.search(r"\b(primary emission|status|location|security|primary cause)\b", message2, re.IGNORECASE)

print(f"Rel 1: {r_match1.group(1) if r_match1 else 'NONE'}")
print(f"Rel 2: {r_match2.group(1) if r_match2 else 'NONE'}")
