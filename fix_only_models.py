# fix_only_models.py
from pathlib import Path

print("🔧 Fixing only models.py...")
print("=" * 60)

models_path = Path("database") / "models.py"

if not models_path.exists():
    print(f"❌ {models_path} not found!")
    exit(1)

with open(models_path, "r", encoding="utf-8") as f:
    content = f.read()

# Check if metadata column exists
if "metadata = Column(JSON" in content:
    print("⚠ Found 'metadata' column in models.py")
    
    # Replace metadata with extra_data
    new_content = content.replace("metadata = Column(JSON, nullable=True)", "extra_data = Column(JSON, nullable=True)")
    new_content = new_content.replace("'metadata': self.metadata", "'extra_data': self.extra_data")
    
    with open(models_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ Fixed: Changed 'metadata' to 'extra_data' in models.py")
else:
    print("✅ models.py already fixed - no 'metadata' column found")

print("\n" + "=" * 60)
print("✅ Fix complete!")
print("=" * 60)
print("\nNow try running: python main.py")