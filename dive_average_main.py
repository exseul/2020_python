import os
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
from src.sim01_PFE.tsk0_sim01_config import ConfigValues as sim01cgf
from common.config_values import ConfigValues as cfg
from common.logger import MPSLogger


log_path = os.path.join(cfg.log_root_dir, 'sim01_PFE')
os.makedirs(log_path, exist_ok=True)
logger = MPSLogger('sim01_PFE', log_path=os.path.join(log_path, 'debug.log')).logger

base_dir = sim01cgf.DIVE_DIR

def calculate_season_average(data):
    """계절별 평균 계산 함수"""
    seasons = {
        'spring': [3, 4, 5],      # 봄
        'summer': [6, 7, 8],      # 여름
        'autumn': [9, 10, 11],    # 가을
        'winter': [12, 1, 2]      # 겨울
    }
    
    for season, months in seasons.items():
        cols = [f"value_{m}" for m in months]
        # 해당 월의 컬럼이 존재하는지 확인하고 평균 계산
        existing_cols = [col for col in cols if col in data.columns]
        if existing_cols:
            data[f"value_{season}"] = data[existing_cols].mean(axis=1)
            logger.info(f"계절 {season} 평균 계산 완료 (사용된 월: {existing_cols})")
        else:
            logger.warning(f"계절 {season}에 해당하는 월별 데이터가 없습니다: {cols}")
    
    return data

def save_seasonal_shapefiles(gdf, scenario, year=None):
    """계절별 shapefile 저장 함수"""
    seasons = ['spring', 'summer', 'autumn', 'winter']
    
    for season in seasons:
        season_col = f"value_{season}"
        if season_col in gdf.columns:
            # 계절별 데이터프레임 생성
            season_gdf = gdf[["x", "y", season_col, "geometry"]].copy()
            season_gdf = season_gdf.rename(columns={season_col: "value"})
            
            # 저장 경로 설정
            if scenario == 'curr':
                output_dir = os.path.join(base_dir, scenario)
                shp_file = os.path.join(output_dir, f"combined_{scenario}_{season}.shp")
            else:
                output_dir = os.path.join(base_dir, scenario, str(year), 'average')
                shp_file = os.path.join(output_dir, f"combined_{scenario}_{year}_{season}.shp")
            
            # 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # shapefile 저장
            season_gdf.to_file(shp_file)
            logger.info(f"계절별 shapefile 저장 완료: {shp_file}")

def calculate_monthly_average(scenario, shp_files, y=None):
    """월별 평균 계산 및 계절별 평균 포함"""
    gdfs = []
    
    # 모든 월별 shp 파일 불러오기
    for m, f in enumerate(shp_files, start=1):
        if not os.path.exists(f):
            logger.warning(f"파일이 존재하지 않습니다: {f}")
            continue
            
        try:
            gdf = gpd.read_file(f)
            gdf = gdf[["x", "y", "value"]]   # geometry는 버림
            gdf = gdf.rename(columns={"value": f"value_{m}"})
            gdfs.append(gdf)
            logger.info(f"월별 데이터 로드 완료: {f}")
        except Exception as e:
            logger.error(f"파일 로드 실패 {f}: {e}")
            continue

    if not gdfs:
        logger.error("로드된 월별 데이터가 없습니다.")
        return

    # x,y 기준으로 병합
    merged = gdfs[0]
    for gdf in gdfs[1:]:
        merged = pd.merge(
            merged, gdf,
            on=["x", "y"],
            how="outer"
        )

    # 연평균 계산
    value_cols = [col for col in merged.columns if col.startswith("value_") and col.split("_")[1].isdigit()]
    merged["value_mean"] = merged[value_cols].mean(axis=1)

    # 계절별 평균 계산
    merged = calculate_season_average(merged)

    # Point geometry 생성
    merged["geometry"] = merged.apply(lambda row: Point(row["x"], row["y"]), axis=1)

    # GeoDataFrame 변환 (좌표계는 원래 shapefile과 동일하게 설정)
    sample_gdf = gpd.read_file(shp_files[0])
    final_gdf = gpd.GeoDataFrame(
        merged,
        geometry="geometry",
        crs=sample_gdf.crs
    )

    # 연평균 shapefile 저장
    if scenario == 'curr':
        output_dir = os.path.join(base_dir, scenario)
        shp_file = os.path.join(output_dir, f"combined_{scenario}_year.shp")
    else:
        output_dir = os.path.join(base_dir, scenario, str(y), 'average')
        shp_file = os.path.join(output_dir, f"combined_{scenario}_{y}_year.shp")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 연평균 데이터만 저장 (x, y, value_mean, geometry)
    annual_gdf = final_gdf[["x", "y", "value_mean", "geometry"]].copy()
    annual_gdf = annual_gdf.rename(columns={"value_mean": "value"})
    annual_gdf.to_file(shp_file)
    logger.info(f"연평균 shapefile 저장 완료: {shp_file}")

    # 계절별 shapefile 저장
    save_seasonal_shapefiles(final_gdf, scenario, y)

def dive_average_main(target_scenarios=[]):
    """메인 실행 함수"""
    scenarios = target_scenarios or []
    try:
        for scenario in scenarios:
            logger.info(f"시나리오 {scenario} 처리 시작")
            
            if scenario == 'curr': # curr 시나리오 처리
                shp_files = [os.path.join(base_dir, scenario, str(m), f"combined_{scenario}_{m}.shp") for m in range(1, 13)]
                calculate_monthly_average(scenario, shp_files)
                logger.info(f"curr 시나리오 처리 완료")
                
            else: # 미래 시나리오 처리
                for y in range(2030, 2061, 10):
                    logger.info(f"시나리오 {scenario}, 연도 {y} 처리 시작")
                    shp_files = [os.path.join(base_dir, scenario, str(y), str(m), f"combined_{scenario}_{y}_{m}.shp") for m in range(1, 13)]
                    calculate_monthly_average(scenario, shp_files, y)
                    logger.info(f"시나리오 {scenario}, 연도 {y} 처리 완료")
                    
        logger.info("모든 시나리오 처리 완료")
    except Exception as e:
        logger.error(f"작업 실행 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    # 예시 실행
    target_scenarios = ['curr', 'scenario1', 'scenario2']  # 실제 시나리오명으로 변경
    dive_average_main(target_scenarios)