"""
PWA 아이콘 생성 스크립트
실행: python create_icons.py
"""
import os

# icons 폴더 생성
os.makedirs('icons', exist_ok=True)

# 간단한 SVG 아이콘 (PNG 대신 SVG 사용)
svg_icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect fill="#0a0e17" width="512" height="512" rx="64"/>
  <circle cx="200" cy="280" r="50" fill="#3b82f6"/>
  <circle cx="312" cy="200" r="50" fill="#f97316"/>
  <path d="M256 80 L256 420" stroke="#94a3b8" stroke-width="4" stroke-dasharray="12 6"/>
  <path d="M150 350 L350 350" stroke="#22c55e" stroke-width="6"/>
</svg>'''

# SVG를 icons 폴더에 저장
with open('icons/icon.svg', 'w', encoding='utf-8') as f:
    f.write(svg_icon)

print("✅ icons/icon.svg 생성 완료!")

# PIL이 설치되어 있으면 PNG도 생성
try:
    from PIL import Image
    import cairosvg
    
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        cairosvg.svg2png(
            bytestring=svg_icon.encode('utf-8'),
            write_to=f'icons/icon-{size}.png',
            output_width=size,
            output_height=size
        )
        print(f"✅ icons/icon-{size}.png 생성 완료!")
    
    print("\n🎉 모든 PNG 아이콘 생성 완료!")
    
except ImportError:
    print("\n⚠️ PNG 아이콘을 생성하려면 다음 명령어로 라이브러리를 설치하세요:")
    print("   pip install pillow cairosvg")
    print("\n또는 온라인 도구를 사용하세요:")
    print("   https://realfavicongenerator.net/")
    print("   https://www.pwabuilder.com/imageGenerator")
    print("\n📌 icons/icon.svg 파일을 업로드하면 PNG 아이콘을 생성할 수 있습니다.")
