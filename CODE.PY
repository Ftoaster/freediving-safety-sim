import tkinter as tk
from tkinter import ttk
import time

class SafetySimulator:
    # --- 상수 정의 ---
    SURFACE_Y = 20
    CANVAS_WIDTH = 600
    CANVAS_HEIGHT = 400
    SCALE_FACTOR = 8  # 1미터당 픽셀 수
    UPDATE_INTERVAL = 50  # ms
    TIMELINE_HEIGHT = 60
    
    def __init__(self, root):
        self.root = root
        self.root.title("Freediving Safety Buddy Simulator")
        self.root.geometry("650x800")

        # --- 변수 초기화 ---
        self.is_running = False
        self.is_paused = False
        self.sim_speed = 1.0
        self.last_update_time = 0
        
        # 시뮬레이션 시간 (실제 시간과 분리)
        self.current_sim_time = 0.0
        self.total_dive_time = 0.0
        
        # 다이버/세이프티 깊이
        self.diver_depth = 0.0
        self.safety_depth = 0.0
        
        # 캐시된 입력값
        self.cached_target = 40.0
        self.cached_meet = 15.0
        self.cached_diver_speed = 1.0
        self.cached_safety_speed = 1.0
        
        # 타임라인 이벤트 시간
        self.turn_time = 0.0
        self.safety_start_time = 0.0
        self.meeting_time = 0.0
        
        # 슬라이더 드래그 상태
        self.is_seeking = False

        # --- UI 레이아웃 ---
        self.create_widgets()
        
        # 초기 화면 그리기
        self.draw_scene()
        
        # 애니메이션 루프 시작
        self.update_simulation()

    def create_widgets(self):
        # 1. 설정 패널 (Input Frame)
        control_frame = ttk.LabelFrame(self.root, text="Dive Plan Settings")
        control_frame.pack(fill="x", padx=10, pady=5)

        # 그리드 설정
        ttk.Label(control_frame, text="Target Depth (m):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_target = ttk.Entry(control_frame, width=10)
        self.entry_target.insert(0, "40")
        self.entry_target.grid(row=0, column=1)

        ttk.Label(control_frame, text="Meeting Depth (m):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_meet = ttk.Entry(control_frame, width=10)
        self.entry_meet.insert(0, "15")
        self.entry_meet.grid(row=0, column=3)

        ttk.Label(control_frame, text="Diver Speed (m/s):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_diver_speed = ttk.Entry(control_frame, width=10)
        self.entry_diver_speed.insert(0, "1.0")
        self.entry_diver_speed.grid(row=1, column=1)

        ttk.Label(control_frame, text="Safety Speed (m/s):").grid(row=1, column=2, padx=5, pady=5)
        self.entry_safety_speed = ttk.Entry(control_frame, width=10)
        self.entry_safety_speed.insert(0, "1.0")
        self.entry_safety_speed.grid(row=1, column=3)
        
        # 배속 설정
        ttk.Label(control_frame, text="Sim Speed (x):").grid(row=2, column=0, padx=5, pady=5)
        self.entry_sim_speed = ttk.Entry(control_frame, width=10)
        self.entry_sim_speed.insert(0, "1.0")
        self.entry_sim_speed.grid(row=2, column=1)

        # 버튼
        self.btn_start = ttk.Button(control_frame, text="▶ Start", command=self.start_sim, width=12)
        self.btn_start.grid(row=3, column=0, pady=10, padx=5)
        
        self.btn_pause = ttk.Button(control_frame, text="⏸ Pause", command=self.toggle_pause, width=12, state="disabled")
        self.btn_pause.grid(row=3, column=1, pady=10, padx=5)
        
        self.btn_reset = ttk.Button(control_frame, text="⏹ Reset", command=self.reset_sim, width=12)
        self.btn_reset.grid(row=3, column=2, pady=10, padx=5)

        # 2. 정보 패널 (Info Frame)
        info_frame = ttk.LabelFrame(self.root, text="Calculation & Status")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_calc = ttk.Label(info_frame, text="계산 결과 대기 중...", foreground="blue")
        self.lbl_calc.pack(pady=5)
        
        self.lbl_timer = ttk.Label(info_frame, text="Dive Time: 0.0s / 0.0s", font=("Arial", 12, "bold"))
        self.lbl_timer.pack(pady=5)
        
        self.lbl_status = ttk.Label(info_frame, text="", font=("Arial", 10))
        self.lbl_status.pack(pady=2)

        # 3. 타임라인 패널
        timeline_frame = ttk.LabelFrame(self.root, text="Timeline")
        timeline_frame.pack(fill="x", padx=10, pady=5)
        
        # 타임라인 캔버스 (이벤트 마커 표시)
        self.timeline_canvas = tk.Canvas(timeline_frame, bg="white", height=self.TIMELINE_HEIGHT)
        self.timeline_canvas.pack(fill="x", padx=5, pady=5)
        
        # 타임라인 슬라이더
        self.timeline_var = tk.DoubleVar(value=0)
        self.timeline_slider = ttk.Scale(
            timeline_frame, 
            from_=0, 
            to=100, 
            orient="horizontal",
            variable=self.timeline_var,
            command=self.on_timeline_change
        )
        self.timeline_slider.pack(fill="x", padx=5, pady=5)
        
        # 슬라이더 마우스 이벤트
        self.timeline_slider.bind("<ButtonPress-1>", self.on_seek_start)
        self.timeline_slider.bind("<ButtonRelease-1>", self.on_seek_end)
        
        # 퀵 점프 버튼
        jump_frame = ttk.Frame(timeline_frame)
        jump_frame.pack(fill="x", padx=5, pady=5)
        
        self.btn_jump_start = ttk.Button(jump_frame, text="⏮ 시작", command=lambda: self.jump_to_time(0), width=10)
        self.btn_jump_start.pack(side="left", padx=2)
        
        self.btn_jump_turn = ttk.Button(jump_frame, text="🔄 턴", command=self.jump_to_turn, width=10)
        self.btn_jump_turn.pack(side="left", padx=2)
        
        self.btn_jump_safety = ttk.Button(jump_frame, text="🏊 세이프티 출발", command=self.jump_to_safety_start, width=12)
        self.btn_jump_safety.pack(side="left", padx=2)
        
        self.btn_jump_meet = ttk.Button(jump_frame, text="🤝 미팅", command=self.jump_to_meeting, width=10)
        self.btn_jump_meet.pack(side="left", padx=2)
        
        self.btn_jump_end = ttk.Button(jump_frame, text="⏭ 종료", command=self.jump_to_end, width=10)
        self.btn_jump_end.pack(side="left", padx=2)

        # 4. 시각화 캔버스 (Canvas)
        self.canvas = tk.Canvas(self.root, bg="alice blue", height=self.CANVAS_HEIGHT)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

    def validate_inputs(self):
        """입력값 유효성 검사"""
        try:
            target = float(self.entry_target.get())
            meet = float(self.entry_meet.get())
            d_speed = float(self.entry_diver_speed.get())
            s_speed = float(self.entry_safety_speed.get())
            sim_speed = float(self.entry_sim_speed.get())
            
            errors = []
            
            if target <= 0:
                errors.append("목표 수심은 양수여야 합니다")
            if meet <= 0:
                errors.append("미팅 수심은 양수여야 합니다")
            if target <= meet:
                errors.append("목표 수심이 미팅 수심보다 깊어야 합니다")
            if d_speed <= 0:
                errors.append("다이버 속도는 양수여야 합니다")
            if s_speed <= 0:
                errors.append("세이프티 속도는 양수여야 합니다")
            if sim_speed <= 0:
                errors.append("시뮬레이션 배속은 양수여야 합니다")
            
            if errors:
                self.lbl_calc.config(text=f"Error: {errors[0]}", foreground="red")
                return False
            
            # 유효성 검사 통과 시 값 캐시
            self.cached_target = target
            self.cached_meet = meet
            self.cached_diver_speed = d_speed
            self.cached_safety_speed = s_speed
            self.sim_speed = sim_speed
            
            return True
            
        except ValueError:
            self.lbl_calc.config(text="Error: 모든 필드에 숫자를 정확히 입력해주세요.", foreground="red")
            return False

    def calculate_plan(self):
        """다이브 계획 및 타임라인 이벤트 계산"""
        target = self.cached_target
        meet = self.cached_meet
        d_speed = self.cached_diver_speed
        s_speed = self.cached_safety_speed
        
        # 타임라인 이벤트 시간 계산
        self.turn_time = target / d_speed
        diver_ascent_to_meet_time = (target - meet) / d_speed
        self.meeting_time = self.turn_time + diver_ascent_to_meet_time
        
        # 세이프티 출발 시간
        safety_time_to_meet = meet / s_speed
        self.safety_start_time = self.meeting_time - safety_time_to_meet
        
        # 전체 다이브 시간 (수면 도착)
        self.total_dive_time = self.turn_time + (target / d_speed)
        
        # 슬라이더 범위 설정
        self.timeline_slider.config(to=self.total_dive_time)
        
        # 턴 타임 기준 대기 시간
        wait_after_turn = self.safety_start_time - self.turn_time
        
        self.lbl_calc.config(
            text=f"[계산 결과] 세이프티 출발: {self.safety_start_time:.1f}초 | "
                 f"턴: {self.turn_time:.1f}초 | 미팅: {self.meeting_time:.1f}초 | "
                 f"총: {self.total_dive_time:.1f}초",
            foreground="blue"
        )
        
        self.draw_timeline()

    def calculate_positions_at_time(self, t):
        """특정 시간에서의 다이버/세이프티 위치 계산"""
        target = self.cached_target
        meet = self.cached_meet
        d_speed = self.cached_diver_speed
        s_speed = self.cached_safety_speed
        
        # 다이버 위치
        if t <= self.turn_time:
            # 하강 중
            diver_depth = d_speed * t
        else:
            # 상승 중
            ascent_time = t - self.turn_time
            diver_depth = target - (d_speed * ascent_time)
            diver_depth = max(0, diver_depth)
        
        # 세이프티 위치
        if t < self.safety_start_time:
            safety_depth = 0
        elif t < self.safety_start_time + (meet / s_speed):
            # 하강 중
            descent_time = t - self.safety_start_time
            safety_depth = s_speed * descent_time
        else:
            # 미팅 지점 도달 후
            safety_depth = meet
            # 다이버가 미팅 지점 지나면 함께 상승
            if diver_depth < meet:
                safety_depth = diver_depth
        
        return diver_depth, safety_depth

    def get_status_at_time(self, t):
        """특정 시간에서의 상태 문자열"""
        if t <= 0:
            return "🏊 준비..."
        elif t < self.turn_time:
            return "🏊 다이버 하강 중..."
        elif t < self.turn_time + 0.5:
            return "🔄 다이버 턴!"
        elif t < self.safety_start_time:
            return "⬆️ 다이버 상승 중 (세이프티 대기)"
        elif t < self.safety_start_time + (self.cached_meet / self.cached_safety_speed):
            return "🏊 세이프티 하강 중!"
        elif t < self.meeting_time:
            return "⏳ 세이프티 미팅 지점 대기"
        elif t < self.total_dive_time:
            return "✅ 미팅 성공! 함께 상승 중"
        else:
            return "🎉 다이브 완료!"

    def draw_timeline(self):
        """타임라인 캔버스에 이벤트 마커 그리기"""
        self.timeline_canvas.delete("all")
        
        if self.total_dive_time <= 0:
            return
        
        canvas_width = self.timeline_canvas.winfo_width()
        if canvas_width < 10:
            canvas_width = 600
        
        padding = 20
        usable_width = canvas_width - (padding * 2)
        
        # 배경 바
        self.timeline_canvas.create_rectangle(
            padding, 25, canvas_width - padding, 35, 
            fill="#e0e0e0", outline=""
        )
        
        # 현재 진행 바
        if self.total_dive_time > 0:
            progress = self.current_sim_time / self.total_dive_time
            progress = min(1, max(0, progress))
            progress_x = padding + (usable_width * progress)
            self.timeline_canvas.create_rectangle(
                padding, 25, progress_x, 35, 
                fill="#4CAF50", outline=""
            )
        
        # 이벤트 마커 함수
        def draw_marker(time_val, color, label, y_offset=0):
            if time_val > self.total_dive_time:
                return
            x = padding + (usable_width * (time_val / self.total_dive_time))
            self.timeline_canvas.create_line(x, 20, x, 40, fill=color, width=2)
            self.timeline_canvas.create_oval(x-4, 26, x+4, 34, fill=color, outline="")
            self.timeline_canvas.create_text(x, 50 + y_offset, text=label, font=("Arial", 8), fill=color)
        
        # 이벤트 마커
        draw_marker(0, "blue", f"시작\n0s")
        draw_marker(self.turn_time, "purple", f"턴\n{self.turn_time:.1f}s")
        draw_marker(self.safety_start_time, "orange", f"세이프티\n{self.safety_start_time:.1f}s")
        draw_marker(self.meeting_time, "green", f"미팅\n{self.meeting_time:.1f}s")
        draw_marker(self.total_dive_time, "red", f"종료\n{self.total_dive_time:.1f}s")
        
        # 현재 위치 마커
        if self.total_dive_time > 0:
            current_x = padding + (usable_width * (self.current_sim_time / self.total_dive_time))
            self.timeline_canvas.create_polygon(
                current_x - 6, 15, current_x + 6, 15, current_x, 23,
                fill="#2196F3", outline=""
            )

    def draw_scene(self):
        """메인 시뮬레이션 캔버스 그리기"""
        self.canvas.delete("all")
        
        target = self.cached_target
        meet = self.cached_meet
        
        # 기본 라인 및 수심 눈금
        self.canvas.create_line(0, self.SURFACE_Y, self.CANVAS_WIDTH, self.SURFACE_Y, fill="blue", width=2)
        self.canvas.create_text(self.CANVAS_WIDTH - 50, 10, text="Surface (0m)")
        
        max_depth_display = target + 10
        center_x = self.CANVAS_WIDTH // 2
        
        # 가이드 로프
        rope_end_y = self.SURFACE_Y + max_depth_display * self.SCALE_FACTOR
        self.canvas.create_line(center_x, self.SURFACE_Y, center_x, rope_end_y, fill="gray", dash=(4, 2))

        # 목표 수심 표시
        target_y = self.SURFACE_Y + target * self.SCALE_FACTOR
        self.canvas.create_line(center_x - 20, target_y, center_x + 20, target_y, fill="red", width=3)
        self.canvas.create_text(center_x + 50, target_y, text=f"Target: {target:.0f}m")

        # 미팅 수심 표시
        meet_y = self.SURFACE_Y + meet * self.SCALE_FACTOR
        self.canvas.create_line(center_x - 15, meet_y, center_x + 15, meet_y, fill="green", width=2, dash=(2, 2))
        self.canvas.create_text(center_x + 50, meet_y, text=f"Meet: {meet:.0f}m", fill="green")

        # 수심 눈금 (10m 단위)
        for depth in range(10, int(max_depth_display), 10):
            y = self.SURFACE_Y + depth * self.SCALE_FACTOR
            self.canvas.create_line(center_x - 5, y, center_x + 5, y, fill="lightgray")
            self.canvas.create_text(center_x - 25, y, text=f"{depth}m", fill="gray", font=("Arial", 8))

        # 다이버 그리기
        diver_pixel_y = self.SURFACE_Y + self.diver_depth * self.SCALE_FACTOR
        self.canvas.create_oval(
            center_x - 10, diver_pixel_y - 10, 
            center_x + 10, diver_pixel_y + 10, 
            fill="blue", outline="darkblue", width=2
        )
        self.canvas.create_text(
            center_x - 40, diver_pixel_y, 
            text=f"Diver\n{self.diver_depth:.1f}m", 
            font=("Arial", 9, "bold"), fill="blue"
        )

        # 세이프티 그리기
        safety_pixel_y = self.SURFACE_Y + self.safety_depth * self.SCALE_FACTOR
        offset_x = 40
        self.canvas.create_oval(
            center_x + offset_x - 10, safety_pixel_y - 10, 
            center_x + offset_x + 10, safety_pixel_y + 10, 
            fill="orange", outline="darkorange", width=2
        )
        self.canvas.create_text(
            center_x + offset_x + 40, safety_pixel_y, 
            text=f"Safety\n{self.safety_depth:.1f}m", 
            font=("Arial", 9, "bold"), fill="darkorange"
        )

    def set_inputs_state(self, state):
        """입력 필드 활성화/비활성화"""
        self.entry_target.config(state=state)
        self.entry_meet.config(state=state)
        self.entry_diver_speed.config(state=state)
        self.entry_safety_speed.config(state=state)
        self.entry_sim_speed.config(state=state)

    def start_sim(self):
        if self.is_running and self.is_paused:
            # 일시정지 상태에서 재시작
            self.toggle_pause()
            return
            
        if not self.validate_inputs():
            return
        
        self.calculate_plan()
        self.current_sim_time = 0.0
        self.diver_depth = 0.0
        self.safety_depth = 0.0
        
        self.set_inputs_state("disabled")
        self.btn_start.config(text="▶ Resume", state="disabled")
        self.btn_pause.config(state="normal")
        
        self.is_running = True
        self.is_paused = False
        self.last_update_time = time.time()

    def toggle_pause(self):
        """일시정지/재개"""
        if not self.is_running:
            return
            
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.btn_pause.config(text="▶ Resume")
            self.btn_start.config(state="normal")
        else:
            self.btn_pause.config(text="⏸ Pause")
            self.btn_start.config(state="disabled")
            self.last_update_time = time.time()

    def reset_sim(self):
        self.is_running = False
        self.is_paused = False
        self.current_sim_time = 0.0
        self.diver_depth = 0.0
        self.safety_depth = 0.0
        
        self.set_inputs_state("normal")
        self.btn_start.config(text="▶ Start", state="normal")
        self.btn_pause.config(text="⏸ Pause", state="disabled")
        
        self.timeline_var.set(0)
        self.draw_scene()
        self.draw_timeline()
        self.lbl_timer.config(text="Dive Time: 0.0s / 0.0s")
        self.lbl_status.config(text="")
        self.lbl_calc.config(text="계산 결과 대기 중...", foreground="blue")

    def on_timeline_change(self, value):
        """슬라이더 값 변경 시"""
        if self.is_seeking and self.total_dive_time > 0:
            self.jump_to_time(float(value))

    def on_seek_start(self, event):
        """슬라이더 드래그 시작"""
        self.is_seeking = True
        if self.is_running and not self.is_paused:
            self.toggle_pause()

    def on_seek_end(self, event):
        """슬라이더 드래그 종료"""
        self.is_seeking = False

    def jump_to_time(self, t):
        """특정 시간으로 점프"""
        if self.total_dive_time <= 0:
            # 시뮬레이션 시작 전이면 먼저 계산
            if not self.validate_inputs():
                return
            self.calculate_plan()
            self.is_running = True
            self.is_paused = True
            self.set_inputs_state("disabled")
            self.btn_start.config(text="▶ Resume", state="normal")
            self.btn_pause.config(text="▶ Resume", state="normal")
        
        t = max(0, min(t, self.total_dive_time))
        self.current_sim_time = t
        self.diver_depth, self.safety_depth = self.calculate_positions_at_time(t)
        
        self.timeline_var.set(t)
        self.update_display()

    def jump_to_turn(self):
        """턴 시점으로 점프"""
        self.jump_to_time(self.turn_time)

    def jump_to_safety_start(self):
        """세이프티 출발 시점으로 점프"""
        self.jump_to_time(self.safety_start_time)

    def jump_to_meeting(self):
        """미팅 시점으로 점프"""
        self.jump_to_time(self.meeting_time)

    def jump_to_end(self):
        """종료 시점으로 점프"""
        self.jump_to_time(self.total_dive_time)

    def update_display(self):
        """화면 업데이트"""
        self.lbl_timer.config(text=f"Dive Time: {self.current_sim_time:.1f}s / {self.total_dive_time:.1f}s")
        self.lbl_status.config(text=self.get_status_at_time(self.current_sim_time), foreground="darkblue")
        self.draw_scene()
        self.draw_timeline()

    def update_simulation(self):
        """메인 업데이트 루프"""
        if self.is_running and not self.is_paused and not self.is_seeking:
            current_time = time.time()
            delta = (current_time - self.last_update_time) * self.sim_speed
            self.last_update_time = current_time
            
            # 시뮬레이션 시간 증가
            self.current_sim_time += delta
            
            # 종료 체크
            if self.current_sim_time >= self.total_dive_time:
                self.current_sim_time = self.total_dive_time
                self.is_running = False
                self.set_inputs_state("normal")
                self.btn_start.config(text="▶ Start", state="normal")
                self.btn_pause.config(state="disabled")
            
            # 위치 계산
            self.diver_depth, self.safety_depth = self.calculate_positions_at_time(self.current_sim_time)
            
            # 슬라이더 위치 업데이트
            self.timeline_var.set(self.current_sim_time)
            
            self.update_display()
        
        self.root.after(self.UPDATE_INTERVAL, self.update_simulation)


if __name__ == "__main__":
    root = tk.Tk()
    app = SafetySimulator(root)
    root.mainloop()
